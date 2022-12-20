import discord
import os
import requests
import json
import random
from replit import db

intents = discord.Intents().all()
client = discord.Client(intents=intents);

sad_words = ["sad", "pain", "depressed", "unhappy", "angry", "miserable", "depressing", "hate school"]

starter_encouragements = [
  "Do not falter, you are on the path to victory.",
  "Rise above, your strength is vast and infinite.",
  "You can go as far as you want."
]

starter_vagabond = [
  "Be aware of yourself, and accept yourself as you are. - Takuan Sōhō",
  "Preoccupied with a single leaf, you won't see the tree. Preoccupied with a single tree,       you'll miss the entire forest. - Takuan Sōhō",
  "The more one tries to look away, the more one gets preoccupied. - Takuan Sōhō",
  "See everything in its entirety, effortlessly. - Takuan Sōhō",
  "So many things in this world cannot be expressed with words. Some things can not be explained, they must be experienced. - Inei Hozoin"
]

if "responding" not in db.keys():
  db["responding"] = True

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " - " + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys(): # if there are encouragements in database
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def update_vagabond(vagabond_quote):
  if "quotes" in db.keys(): # if there are quotes in database
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

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  msg = message.content
  user = message.author
  
  if user == client.user:
    return
    
  if msg.startswith('$insight'):
    quote = get_quote()
    await message.channel.send(user.mention + " " + quote)

  if msg.startswith('$vagabond'):
    await message.channel.send(random.choice(starter_vagabond))

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"].value
  
    if any(word in msg for word in sad_words):
      await message.channel.send(user.mention + " " + random.choice(options))

  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ", 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New insight has been added.")

  if msg.startswith("$vnew"):
    vagabond_quote = msg.split("$newv ", 1)[1]
    update_vagabond(vagabond_quote)
    await message.channel.send("New quote has been added.")

  if msg.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements.value)

  if msg.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements.value)

  if msg.startswith("$responding"):
    value = msg.split("$responding ",1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")
      
client.run(os.getenv('TOKEN'))

