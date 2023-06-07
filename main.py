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
bot = commands.Bot(command_prefix="~", intents=intents, application_id=config['app_id'])

messages = OrderedDict({
    "wann": ["An einem elitären Zeitpunkt", "¯\\_(ツ)_/¯"] + [lambda: f"<t:{int(get_next_tut()[0])}:R> ~ <t:{int(get_next_tut()[1])}:R>"] * 3,
    "warum": ["Warum nicht?", "trivial. ■"],
    "wogegen konvergiert": ["???", "Übungsschein", "hoffentlich bestandene LA Klausur"],
    "wofür": ["Für Kühnlein!", "Mathebau"],
    "worüber" : ["glücklicherweise _nicht_ MS Teams", "vermutlich über 20.30 SR 2.061 (noch nicht bewiesen)"],
    "wer": ["Johannes, unser Herr und Meister", "Der Zirkel der LA-Lernenden"],
    "wieso": ["wieso muss ich das beantworten?", "Für die memes", "µ̴̛̰̖̩̖̪̫͔̥͚͌̄́̎͂̊̆̕̕͜m̷̢͓̩͓̲̝̭̹̪̬̂͊̅͌̋̈́̓̚̚̕ ̵̢̨̧̣̩̳̖͎͈̘̐͛̊́̎͌͑̓͛͠Ļ̵̞̻̗̰̫̺̯̥̉̃̀̍̌̏̄̓̉͘ͅÄ̵̟̖͙̮͕͉̟̹͍͕̈́͗̓̽̓̋̀̔͐͝ ̵̡̦̭̹̖̤̥̪͔̌̌́͌̾͑̑̇̚͝ͅz̸̢̢̭̺̰͓̦̫̙͓͆̉̒͊͂̊̆̊͑̅µ̷̰̭̟̺̳͎͔͇̭̬̇̒́͊͂̽̀̑̏͘ ̷̮̫̲͍̲̜̞͔͖̯̃̽̓̈́̽͛̈́̄̓͝ß̷̤̮̣͍͉̱͕͔̝̝̽̓͆͊̌͗́̃̌͝ề̴̼̩̦̱̱̯̫͚͚̩͋͛͐̈́̚͘̚͝͠§̴̢̨̢̛̛̩̰̱͈̪̹̼̈́̋̏̓͊̃̕͝†̴̨̨̦̖̗̲̼̰̯͖̾̎̈̆̒̒͆͛͗͌ę̸̛̩̬̼̮̹̩̖̫͍̂̋̓́́́͂͋̕͘ḩ̶̨̛̮͈͎̘͎̘͎̰̂̊̇̄̽͒̍̄͊ȩ̴̹̗̝̙͓͉͉̖̣̂̋̿̀̌̽̌͗̆̊͝ñ̴̡̪̮͎̗͇̥̭͇̘̐̀̈̀͆̂̋̏̇͊"],
    "was": ["https://iwgtfy.com/?q=Was+ist+ein+Tutorium", "dies und das und das Standardskalarprodukt (siehe 11.1.3)"],
    "wo": ["Mathebau", "20.30 SR 3.061", r"https://www.kit.edu/campusplan/?id=20%2E30&label=20%2E30+SR+%2D1%2E011+%28UG%29+%E2%80%93+Tutorien+Lineare+Algebra+2+f%C3%BCr+Informatik+und+Mathematik"],
})

assignment_added = "Neues Übungsblatt: ``{file}``, Abgabe am  {date}"
assignment_updated = "``{file}`` wurde aktualisiert. Version: ``{version}``, Abgabedatum {date}"

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
    check_files.start()
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


async def send_to_channel(file, message):
    channel = bot.get_channel(int(config["update_channel_id"]))
    f = discord.File(config["assignment_path"] + file)
    await channel.send(message, file=f)


@tasks.loop(hours=1)
async def check_files():
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
                data["assignments"][file] = {"ver": 1, "last_change": datetime.now().timestamp(), "hash": filehash}
                await send_to_channel(file, assignment_added.format(file=file, date=date))
                change = True
            else:
                # check if file hash has changed
                with open(path + file, "rb") as f:
                    filehash = hashlib.sha1(f.read()).hexdigest()

                if filehash != data["assignments"][file]["hash"]:
                    date = get_due_date(path + file)
                    data["assignments"][file]["ver"] += 1
                    data["assignments"][file]["last_change"] = datetime.now().timestamp()
                    data["assignments"][file]["hash"] = filehash
                    message = assignment_updated.format(file=file, date=date, version=data["assignments"][file]["ver"])
                    await send_to_channel(file, message)
                    change = True


        for _, _, files in os.walk(path):
            for file in files:
                # check if file hash has changed
                with open(path + file, "rb") as f:
                    filehash = hashlib.sha1(f.read()).hexdigest()

                if filehash != data["script"]["hash"]:
                    data["script"]["ver"] += 1
                    data["script"]["last_change"] = datetime.now().timestamp()
                    data["script"]["hash"] = filehash
                    message = f"Neue Version des Skripts: ``V{data['script']['ver']}``"
                    await send_to_channel(file, message)
                    change = True
                    
    # update data file
    if change:
        with open("./data.json", "w") as f:
            json.dump(data, f, indent=4)


def setup():
    if not os.path.exists("./data.json"):
        with open("./data.json", "w") as f:
            f.write('{"assignments": {}}')
    # create script key if it does not exist
    with open("./data.json", "r") as f:
        data = json.load(f)
        if "script" not in data.keys():
            data["script"] = {"ver": 0, "last_change": datetime.now().timestamp(), "hash": ""}
            with open("./data.json", "w") as f:
                json.dump(data, f, indent=4)
        


async def main():
    async with bot:
        await bot.start(config['token'], reconnect=True)


if __name__ == "__main__":
    setup()
    asyncio.run(main())
