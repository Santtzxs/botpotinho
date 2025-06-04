import discord
from discord.ext import commands
import random

class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ship')
    async def ship(self, ctx, membro1: discord.Member, membro2: discord.Member):
        percent = random.randint(0, 100)

        if membro1 == membro2:
            return await ctx.send("❌ Você não pode shippar a mesma pessoa consigo mesma.")

        coracao = "💔"
        if percent > 70:
            coracao = "❤️"
        elif percent > 40:
            coracao = "💖"
        elif percent > 20:
            coracao = "💞"

        embed = discord.Embed(
            title="💘 Compatibilidade Amorosa",
            description=f"{membro1.mention} {coracao} {membro2.mention}\n**Compatibilidade:** {percent}%",
            color=discord.Color.magenta()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ship(bot))
