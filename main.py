import discord
from discord.ext import commands
import asyncio
import configparser
from next_tut import get_next_tut
import random
from collections import OrderedDict

config = configparser.ConfigParser()
config.read("secrets.cfg")
config = config['DEFAULT']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix="~", intents=intents, application_id=config['app_id'])

messages = OrderedDict({
    "wann": ["An einem elitären Zeitpunkt", "¯\\_(ツ)_/¯"] + [lambda : f"<t:{int(get_next_tut()[0])}:R> ~ <t:{int(get_next_tut()[1])}:R>"] * 3,
    "warum" : ["Warum nicht?", "trivial. ■"],
    "wogegen konvergiert": ["???"],
    "wofür" : ["Für Kühnlein!", "Mathebau"],
    "wer" : ["Johannes, unser Herr und Meister"],
    "wieso": ["wieso muss ich das beantworten?", "Für die memes", "µ̴̛̰̖̩̖̪̫͔̥͚͌̄́̎͂̊̆̕̕͜m̷̢͓̩͓̲̝̭̹̪̬̂͊̅͌̋̈́̓̚̚̕ ̵̢̨̧̣̩̳̖͎͈̘̐͛̊́̎͌͑̓͛͠Ļ̵̞̻̗̰̫̺̯̥̉̃̀̍̌̏̄̓̉͘ͅÄ̵̟̖͙̮͕͉̟̹͍͕̈́͗̓̽̓̋̀̔͐͝ ̵̡̦̭̹̖̤̥̪͔̌̌́͌̾͑̑̇̚͝ͅz̸̢̢̭̺̰͓̦̫̙͓͆̉̒͊͂̊̆̊͑̅µ̷̰̭̟̺̳͎͔͇̭̬̇̒́͊͂̽̀̑̏͘ ̷̮̫̲͍̲̜̞͔͖̯̃̽̓̈́̽͛̈́̄̓͝ß̷̤̮̣͍͉̱͕͔̝̝̽̓͆͊̌͗́̃̌͝ề̴̼̩̦̱̱̯̫͚͚̩͋͛͐̈́̚͘̚͝͠§̴̢̨̢̛̛̩̰̱͈̪̹̼̈́̋̏̓͊̃̕͝†̴̨̨̦̖̗̲̼̰̯͖̾̎̈̆̒̒͆͛͗͌ę̸̛̩̬̼̮̹̩̖̫͍̂̋̓́́́͂͋̕͘ḩ̶̨̛̮͈͎̘͎̘͎̰̂̊̇̄̽͒̍̄͊ȩ̴̹̗̝̙͓͉͉̖̣̂̋̿̀̌̽̌͗̆̊͝ñ̴̡̪̮͎̗͇̥̭͇̘̐̀̈̀͆̂̋̏̇͊"],
    "was": ["https://iwgtfy.com/?q=Was+ist+ein+Tutorium", "dies und das und das Standardskalarprodukt (siehe 11.1.3)"],
    "wo": ["Mathebau", "20.30 SR 3.061", r"https://www.kit.edu/campusplan/?id=20%2E30&label=20%2E30+SR+%2D1%2E011+%28UG%29+%E2%80%93+Tutorien+Lineare+Algebra+2+f%C3%BCr+Informatik+und+Mathematik"],
})

def is_tut_msg(message, keywords):
    for key in keywords:
        if not key in message.content.lower():
            return False
    return True

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.competing, name="LA Klausur")
    await bot.change_presence(activity=activity, status=discord.enums.Status.online)

    await bot.tree.sync()
    print("ready~")
        
        
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    for key in messages.keys():
        if is_tut_msg(message, key.split()):
            result = random.choice(messages[key])
            if type(result) == str:
                await message.channel.send(result)
                return
            else:
                await message.channel.send(result())
                return


async def main():
    async with bot:
        await bot.start(config['token'], reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
