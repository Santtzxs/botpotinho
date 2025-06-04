import discord
from discord.ext import commands
import ast
import operator as op

class Calc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="calc")
    async def calc(self, ctx, *, expression: str):
        try:
            # Operadores suportados
            operators = {
                ast.Add: op.add,
                ast.Sub: op.sub,
                ast.Mult: op.mul,
                ast.Div: op.truediv,
                ast.Pow: op.pow,
                ast.Mod: op.mod,
                ast.USub: op.neg,
                ast.UAdd: op.pos
            }

            def eval_node(node):
                if isinstance(node, ast.Constant):  
                    return node.value
                elif isinstance(node, ast.Num):  
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return operators[type(node.op)](eval_node(node.operand))
                else:
                    raise TypeError(f"Tipo de nó não suportado: {type(node)}")

            # Parse da expressão
            tree = ast.parse(expression, mode='eval')
            resultado = eval_node(tree.body)
            
            await ctx.send(f"🧮 Resultado: `{resultado}`")
        
        except Exception as e:
            await ctx.send(f"❌ Expressão inválida ou erro: {str(e)}")

async def setup(bot):
    await bot.add_cog(Calc(bot))