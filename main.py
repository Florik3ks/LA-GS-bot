import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import configparser
from next_tut import get_next_tut
import random

config = configparser.ConfigParser()
config.read("secrets.cfg")
config = config['DEFAULT']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix="~", intents=intents, application_id=config['app_id'])

tut_wann = ["wann tut", "tut wann", "wann wieder tut", "tut wieder wann"]
wann_choices = ["An einem elitären Zeitpunkt", "¯\\_(ツ)_/¯"]
tut_wo = ["wo tut", "tut wo", "wo wieder tut", "tut wieder wo""]
wo_choices = ["Mathebau", "20.30 SR 3.061", r"https://www.kit.edu/campusplan/?id=20%2E30&label=20%2E30+SR+%2D1%2E011+%28UG%29+%E2%80%93+Tutorien+Lineare+Algebra+2+f%C3%BCr+Informatik+und+Mathematik"]

def is_tut_msg(message, options):
    for msg in options:
        if msg in message.content.lower():
            return True
    return False

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
    if is_tut_msg(message, tut_wann):
        tut = get_next_tut()
        tut_msg = f"<t:{int(tut[0])}:R> ~ <t:{int(tut[1])}:R>"
        choices = wann_choices + [tut_msg] * 3
        await message.channel.send(random.choice(choices))
    elif is_tut_msg(message, tut_wo):
        await message.channel.send(random.choice(wo_choices))


async def main():
    async with bot:
        await bot.start(config['token'], reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
