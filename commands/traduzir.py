import discord
from discord.ext import commands
from deep_translator import GoogleTranslator

class Traduzir(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="traduzir")
    async def traduzir(self, ctx, idioma: str, *, texto: str):
        try:
            traduzido = GoogleTranslator(source="auto", target=idioma).translate(texto)

            embed = discord.Embed(title="Tradução", color=discord.Color.green())
            embed.add_field(name="Original", value=texto, inline=False)
            embed.add_field(name="Traduzido", value=traduzido, inline=False)
            embed.set_footer(text=f"Traduzido para '{idioma}'")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao tentar traduzir: {str(e)}")

async def setup(bot):
    await bot.add_cog(Traduzir(bot))
