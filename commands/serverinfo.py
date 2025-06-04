import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        guild = ctx.guild

        embed = discord.Embed(
            title=f"Informações do servidor: {guild.name}",
            color=discord.Color.blue()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👥 Membros", value=guild.member_count, inline=True)
        embed.add_field(name="📆 Criado em", value=guild.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        embed.add_field(name="👑 Dono", value=str(guild.owner), inline=True)
        embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
