import discord
from discord.ext import commands
import aiohttp

class Abracar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='abraçar')
    async def abracar(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.purrbot.site/v2/img/sfw/hug/gif') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(description=f"{ctx.author.mention} abraçou {membro.mention} 🤗", color=discord.Color.purple())
                    embed.set_image(url=data['link'])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Não consegui obter uma imagem de abraço no momento.")


async def setup(bot):
    await bot.add_cog(Abracar(bot))
