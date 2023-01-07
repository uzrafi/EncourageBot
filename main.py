import discord
import os
import random
from discord.ext import commands
import requests
import json
import random
from replit import db
from discord.ui import Button, View
from auth import authenticate

intents = discord.Intents().all()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SEC')

bot = commands.Bot(command_prefix=".", intents=intents)
bot.remove_command('help')

help_guide = json.load(open("help.json"))

sad_words = [
  "sad", "pain", "depressed", "unhappy", "angry", "miserable", "depressing",
  "hate school"
]

starter_encouragements = [
  "Do not falter, you are on the path to victory.",
  "Rise above, your strength is vast and infinite.",
  "You can go as far as you want."
]

starter_vagabond = [
  "Be aware of yourself, and accept yourself as you are. - Takuan Sōhō",
  "Preoccupied with a single leaf, you won't see the tree. Preoccupied with a single tree, you'll miss the entire forest. - Takuan Sōhō",
  "The more one tries to look away, the more one gets preoccupied. - Takuan Sōhō",
  "See everything in its entirety, effortlessly. - Takuan Sōhō",
  "So many things in this world cannot be expressed with words. Some things cannot be explained, they must be experienced. - Inei Hozoin"
]

if "responding" not in db.keys():
  db["responding"] = True


def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " - " + json_data[0]['a']
  return (quote)


def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():  # if there are encouragements in database
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]


def update_vagabond(vagabond_quote):
  if "quotes" in db.keys():  # if there are quotes in database
    quotes = db["quotes"]
    quotes.append(vagabond_quote)
    db["quotes"] = quotes
  else:
    db["quotes"] = [vagabond_quote]


def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements


def delete_vagabond(index):
  quotes = db["quotes"]
  if len(quotes) > index:
    del quotes[index]
    db["quotes"] = quotes


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
  msg = message.content
  user = message.author

  if user == bot.user:
    return

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"].value

    if any(word in msg for word in sad_words):
      await message.channel.send(user.mention + " " + random.choice(options))

  await bot.process_commands(message)


@bot.command()
async def insight(ctx):
  quote = get_quote()
  await ctx.send(ctx.author.mention + " " + quote)


@bot.command()
async def vagabond(ctx):
  await ctx.send(random.choice(starter_vagabond))


@bot.command()
async def responding(ctx, state):
  if state == "true":
    db["responding"] = True
    await ctx.send("Responding is on.")
  elif state == "false":
    db["responding"] = False
    await ctx.send("Responding is off.")
  else:
    await ctx.send("Responding state must be either 'true' or 'false'!")


@bot.command()
async def inew(ctx, encouraging_message):
  encouraging_message = ctx.message.content.split(".enew ", 1)[1]
  update_encouragements(encouraging_message)
  await ctx.send("New insight has been added.")


@bot.command()
async def vnew(ctx, vagabond_quote):
  vagabond_quote = ctx.message.content.split(".vnew ", 1)[1]
  update_vagabond(vagabond_quote)
  await ctx.send("New quote has been added.")


@bot.command()
async def idel(ctx, index):
  if "encouragements" in db.keys():
    delete_encouragement(int(index) - 1)
  await ctx.send("Encouragement #" + index + " has been deleted.")


@bot.command()
async def vdel(ctx, index):
  if "quotes" in db.keys():
    delete_vagabond(int(index) - 6)
  await ctx.send("Vagabond quote #" + index + " has been deleted.")


@bot.command()
async def ilist(ctx):
  list = "```"
  index = 0
  for i in db["encouragements"]:
    index += 1
    list += "Insight #" + str(index) + ": - " + i + "\n"
  await ctx.send(list + "```")


@bot.command()
async def vlist(ctx):
  vquotes = "```"
  vuserq = ""
  index = 0
  for i in starter_vagabond:
    index += 1
    vquotes += "Quote #" + str(index) + ": - " + i + "\n"
  for quotes in db["quotes"]:
    index += 1
    vuserq += "Quote #" + str(index) + ": - " + quotes + "\n"
  await ctx.send(vquotes + vuserq + "```")


@bot.command()
async def vpanel(ctx):
  client = authenticate()
  links = []

  for album in client.get_account_albums('me'):
    for image in client.get_album_images(album.id):
      links.append(image.link)
    break

  await ctx.send(random.choice(links))


def createHelpEmbed(page_num=0, inline=False):
  page_num = page_num % len(list(help_guide))
  page_title = list(help_guide)[page_num]
  e= discord.Embed(colour=0x0e5fe3, title=page_title)
  for key, val in help_guide[page_title].items():
    e.add_field(name=bot.command_prefix+key, value=val, inline=inline)
    e.set_footer(text=f"Page {page_num + 1} of {len(list(help_guide))}")
  return e
    

@bot.command()
async def help(ctx):
  current_page = 0

  async def nextCallback(interaction):
    nonlocal current_page, sent_msg
    current_page += 1
    await sent_msg.edit(embed=createHelpEmbed(page_num=current_page), view=myview)

  async def previousCallback(interaction):
    nonlocal current_page, sent_msg
    current_page -= 1
    await sent_msg.edit(embed=createHelpEmbed(page_num=current_page), view=myview)
  
  next_button = Button(label=">", style= discord.ButtonStyle.blurple)
  next_button.callback = nextCallback
  previous_button = Button(label="<", style= discord.ButtonStyle.blurple)
  previous_button.callback = previousCallback

  myview = View(timeout=180)
  myview.add_item(previous_button)
  myview.add_item(next_button)
  sent_msg = await ctx.send(embed=createHelpEmbed(page_num=0), view=myview)

bot.run(os.getenv('TOKEN'))
