import discord
from discord.ext import commands
import aiohttp

class Beijar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='beijar')
    async def beijar(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author

        if membro == ctx.author:
            return await ctx.send("😳 Você não pode se beijar... ou pode?")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://purrbot.site/api/img/sfw/kiss/gif") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(
                        description=f"💋 {ctx.author.mention} beijou {membro.mention}!",
                        color=discord.Color.pink()
                    )
                    embed.set_image(url=data["link"])
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Não consegui buscar a imagem de beijo agora.")


async def setup(bot):
    await bot.add_cog(Beijar(bot))
