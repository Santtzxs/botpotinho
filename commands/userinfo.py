import discord
from discord.ext import commands

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Informações de {member}", color=0x00ff00)
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Nome", value=member.name, inline=True)
        embed.add_field(name="Apelido", value=member.display_name, inline=True)
        embed.add_field(name="Conta criada em", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        embed.add_field(name="Entrou no servidor em", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
