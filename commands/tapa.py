import discord
from discord.ext import commands
import aiohttp

class Tapa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tapa')
    async def tapa(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author

        if membro == ctx.author:
            return await ctx.send("😐 Você quer se bater? Que triste...")

        url = "https://nekos.life/api/v2/img/slap"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(
                        description=f"👋 {ctx.author.mention} deu um tapa em {membro.mention}!",
                        color=discord.Color.orange()
                    )
                    embed.set_image(url=data["url"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Não consegui buscar a imagem de tapa agora.")

async def setup(bot):
    await bot.add_cog(Tapa(bot))
