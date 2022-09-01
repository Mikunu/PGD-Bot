import discord
from discord.ext import commands

from bot import client


class CogLoader(commands.Cog, description='Управление модулями'):

    def __init__(self, client):
        self.client = client

    @commands.group(aliases=['l'], brief='Управление модулями')
    @commands.has_role('Админ')
    async def loader(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @loader.command(brief='Загружает модуль')
    @commands.has_role('Админ')
    async def load(self, ctx, extension):
        if extension == 'cog_loader.py':
            ctx.reply('Данный модуль защищен от работы с ним.', delete_after=10)
            return
        client.load_extension(f'cogs.{extension}')

    @loader.command(brief='Выгружает модуль')
    @commands.has_role('Админ')
    async def unload(self, ctx, extension):
        if extension == 'cog_loader.py':
            ctx.reply('Данный модуль защищен от работы с ним.', delete_after=10)
            return
        client.unload_extension(f'cogs.{extension}')

    @loader.command(brief='Перезагружает модуль')
    @commands.has_role('Админ')
    async def reload(self, ctx, extension):
        if extension == 'cog_loader.py':
            ctx.reply('Данный модуль защищен от работы с ним.', delete_after=10)
            return
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')


def setup(client):
    client.add_cog(CogLoader(client))
