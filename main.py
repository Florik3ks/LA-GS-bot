import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import configparser
from next_tut import get_next_tut

config = configparser.ConfigParser()
config.read("secrets.cfg")
config = config['DEFAULT']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix="~", intents=intents, application_id=config['app_id'])

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
    if "tut wann" in message.content.lower() or "wann tut" in message.content.lower():
        tut = get_next_tut()
        await message.channel.send(f"<t:{int(tut[0])}:R> ~ <t:{int(tut[1])}:R>")


async def main():
    async with bot:
        await bot.start(config['token'], reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
