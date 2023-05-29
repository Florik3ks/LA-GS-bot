import os
import json
import random
import asyncio
import discord
import hashlib
import configparser
from datetime import datetime
from next_tut import get_next_tut
from collections import OrderedDict
from discord.ext import commands, tasks
from get_assignment_due_date import get_due_date

config = configparser.ConfigParser()
config.read("secrets.cfg", encoding='utf-8')
config = config['DEFAULT']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix="~", intents=intents,
                   application_id=config['app_id'])

messages = OrderedDict({
    "wann": ["An einem elitären Zeitpunkt", "¯\\_(ツ)_/¯"] + [lambda: f"<t:{int(get_next_tut()[0])}:R> ~ <t:{int(get_next_tut()[1])}:R>"] * 3,
    "warum": ["Warum nicht?", "trivial. ■"],
    "wogegen konvergiert": ["???"],
    "wofür": ["Für Kühnlein!", "Mathebau"],
    "wer": ["Johannes, unser Herr und Meister"],
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
    activity = discord.Activity(
        type=discord.ActivityType.competing, name="LA Klausur")
    await bot.change_presence(activity=activity, status=discord.enums.Status.online)
    check_assignments.start()
    print("ready~")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    for key in messages.keys():
        if is_tut_msg(message, [key] + ["tut"]):
            result = random.choice(messages[key])
            if type(result) == str:
                await message.channel.send(result)
                return
            else:
                await message.channel.send(result())
                return


async def send_to_channel(file, date, ver=1):
    channel = bot.get_channel(int(config["update_channel_id"]))
    f = discord.File(config["assignment_path"] + file)
    if ver > 1:
        await channel.send(f"``{file}`` wurde aktualisiert. Version: ``{ver}``, Abgabedatum {date}", file=f)
    await channel.send(f"Neues Übungsblatt: ``{file}``, Abgabe am {date}", file=f)


@tasks.loop(minutes=20)
async def check_assignments():
    # load files (https://github.com/Garmelon/PFERD)
    os.popen("pferd").read()
    change = False
    with open("./data.json", "r") as f:
        data = json.load(f)

    path = config['assignment_path']
    # iterate over pdf files in assignment folder
    for _, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".pdf"):
                continue
            # check whether file is already in data
            if file not in data["assignments"].keys():
                date = get_due_date(path + file)
                with open(path + file, "rb") as f:
                    filehash = hashlib.sha1(f.read()).hexdigest()
                data["assignments"][file] = {
                    "ver": 1, "last_change": datetime.now().timestamp(), "hash": filehash}
                await send_to_channel(file, date)
                change = True
            else:
                # # check if file hash has changed
                with open(path + file, "rb") as f:
                    filehash = hashlib.sha1(f.read()).hexdigest()

                if filehash != data["assignments"][file]["hash"]:
                    date = get_due_date(path + file)
                    data["assignments"][file]["ver"] += 1
                    data["assignments"][file]["last_change"] = datetime.now().timestamp()
                    data["assignments"][file]["hash"] = filehash
                    await send_to_channel(file, date, data["assignments"][file]["ver"])
                    change = True

    # update data file
    if change:
        with open("./data.json", "w") as f:
            json.dump(data, f)


def setup():
    if not os.path.exists("./data.json"):
        with open("./data.json", "w") as f:
            f.write('{"assignments": {}}')


async def main():
    async with bot:
        await bot.start(config['token'], reconnect=True)


if __name__ == "__main__":
    setup()
    asyncio.run(main())
