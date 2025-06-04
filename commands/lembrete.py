import discord
from discord.ext import commands
import asyncio
import re

class Lembrete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_tempo(self, tempo_str):
        match = re.match(r"(\d+)([smh])", tempo_str.lower())
        if not match:
            return None
        quantidade, unidade = match.groups()
        quantidade = int(quantidade)
        if unidade == "s":
            return quantidade
        elif unidade == "m":
            return quantidade * 60
        elif unidade == "h":
            return quantidade * 3600
        return None

    @commands.command(name="lembrete")
    async def lembrete(self, ctx, tempo: str, *, mensagem: str):
        segundos = self.parse_tempo(tempo)
        if segundos is None:
            await ctx.send("❌ Formato inválido! Use algo como 10s, 5m ou 2h.")
            return
        
        await ctx.send(f"⏰ Certo {ctx.author.mention}, vou te lembrar em {tempo}!")
        await asyncio.sleep(segundos)
        await ctx.send(f"🔔 {ctx.author.mention}, aqui está seu lembrete: {mensagem}")

async def setup(bot):
    await bot.add_cog(Lembrete(bot))
