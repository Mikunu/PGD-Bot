import discord
from discord.ext import commands
import random


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='uni',
                      help='uni | Решает, ехать на пары или нет',
                      brief='Решает, ехать на пары или нет')
    async def uni(self, ctx: discord.ext.commands.Context):
        if random.randint(1, 20) > 12:
            await ctx.reply('Отдохни, сегодня тяжелый день, в вузе явно делать нечего')
        else:
            file = discord.File("nofate.jpg")
            await ctx.reply('Не время отдыхать, вуз ждёт!', file=file)

    @commands.command(name='pgd')
    async def pgd(self, ctx: discord.ext.commands.Context):
        await ctx.reply(':heart:')


def setup(client):
    client.add_cog(Fun(client))
