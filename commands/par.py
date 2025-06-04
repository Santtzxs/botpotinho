import discord
from discord.ext import commands
import random

class Par(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='par')
    async def par(self, ctx, cargo: discord.Role = None):
        if not cargo:
            return await ctx.send("❌ Você precisa mencionar um cargo. Ex: `p!par @Cargo`")

        membros = [m for m in cargo.members if not m.bot]

        if len(membros) < 2:
            return await ctx.send("❌ Não há membros suficientes com esse cargo para formar um par.")

        par_sorteado = random.sample(membros, 2)

        embed = discord.Embed(
            title="💑 Par Romântico",
            description=f"✨ {par_sorteado[0].mention} + {par_sorteado[1].mention} = Casal do ano!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Par(bot))
