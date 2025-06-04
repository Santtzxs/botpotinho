from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📚 Ajuda - Comandos do Potinho",
            description="Aqui estão todos os comandos disponíveis!\n\n✨ **Use com carinho.**",
            color=discord.Color.purple()
        )

        # 📌 Utilitários
        embed.add_field(
            name="🔧 Utilitários", 
            value=(
                "🔹 **p!ping** – Testa a latência do bot\n"
                "🎲 **p!roll [número]** – Rola um dado até o número escolhido (padrão 6)\n"
                "👤 **p!userinfo [@usuário]** – Mostra informações do usuário\n"
                "🏠 **p!serverinfo** – Mostra informações do servidor\n"
                "🖼️ **p!avatar [@usuário]** – Mostra o avatar do usuário\n"
                "⏰ **p!lembrete [tempo] [mensagem]** – Define um lembrete (ex: `p!lembrete 10m beber água`)\n"
                "🧠 **p!calc [expressão]** – Calcula expressões matemáticas (ex: `p!calc 5*3+(2^3)`)\n"
                "🌐 **p!traduzir [idioma] [texto]** – Traduz o texto para o idioma desejado (ex: `p!traduzir en Olá mundo`)"
            ), 
            inline=False
        )

        # Espaçamento entre seções
        embed.add_field(name="\u200b", value="\u200b", inline=False)  

        # 🎵 Música (atualizado)
        embed.add_field(
            name="🎶 Música", 
            value=(
                "🔊 **p!entrar** – Entra no canal de voz\n"
                "🚪 **p!sair** – Sai do canal de voz\n"
                "▶️ **p!tocar [URL]** – Toca uma música do YouTube\n"
                "🔁 **p!pular** – Pula uma música da fila\n"
                "⏸️ **p!pausar** – Pausa a música atual\n"
                "▶️ **p!continuar** – Continua a música pausada\n"
                "⏹️ **p!parar** – Para a música e limpa a fila\n"
                "📜 **p!fila** – Mostra a fila de reprodução"
            ),
            inline=False
        )

        # Espaçamento entre seções
        embed.add_field(name="\u200b", value="\u200b", inline=False)  

        # 🎉 Social / Interações
        embed.add_field(
            name="💞 Social & Interações", 
            value=(
                "🤗 **p!abraçar [@usuário]** – Envia um abraço bem apertado\n"
                "💋 **p!beijar [@usuário]** – Dá um beijinho virtual\n"
                "👋 **p!tapa [@usuário]** – Dá um tapinha (de leve, viu?)\n"
                "❤️ **p!ship [@usuário1] [@usuário2]** – Calcula o amor entre dois usuários\n"
                "🎯 **p!par [@cargo]** – Sorteia dois membros com o cargo escolhido"
            ),
            inline=False
        )

        embed.set_footer(text="Desenvolvido com 💖 por Victor Santucci | Use o prefixo p! antes de cada comando.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))