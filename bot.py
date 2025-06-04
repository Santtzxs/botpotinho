import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="p!", intents=intents, help_command=None)


async def load_extensions():
    await bot.load_extension("commands.ping")
    await bot.load_extension("commands.avatar")
    await bot.load_extension("commands.userinfo")
    await bot.load_extension("commands.serverinfo")
    await bot.load_extension("commands.roll")
    await bot.load_extension("commands.help")
    await bot.load_extension("commands.abracar")
    await bot.load_extension("commands.beijar")
    await bot.load_extension("commands.tapa")
    await bot.load_extension("commands.ship")
    await bot.load_extension("commands.par")
    await bot.load_extension("commands.calc")
    await bot.load_extension("commands.lembrete")
    await bot.load_extension("commands.traduzir")
    await bot.load_extension("commands.music")


@bot.event
async def on_ready():
    print(f'Bot conectado como: {bot.user.name}')


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
