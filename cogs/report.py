import os
import requests
import discord
from discord.ext import commands
from bot import client


class Report(commands.Cog, description='Команды багов и TODO'):

    def __init__(self, client):
        self.client = client

    @commands.group(aliases=['r'], enable=False)
    async def report(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @report.command()
    async def bug(self, ctx, *, arg):
        pass
    '''
    async def bug(self, ctx, *, arg):
        url = "https://api.trello.com/1/checklists/61ad2842683b701839df0e61/checkItems"
        headers = {
            "Accept": "application/json"
        }
        author = f'{ctx.author.name}#{ctx.author.discriminator}'
        new_check = f'[{author}] {arg}'
        querystring = {"key": os.environ['TRELLO_KEY'],
                       "token": os.environ['TRELLO_TOKEN'],
                       "name": new_check}
        mikunu: discord.User = client.get_user(302734324648902657)

        message_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}'
        mikunu_msg = f'New bug-report:\nAuthor: {author}\n' \
                     f'In channel: {ctx.channel}\nMessage link: {message_link}\n{arg}'
        response = requests.post(url, headers=headers, params=querystring)
        await ctx.reply('Баг-репорт отравлен')
        if response.status_code != 200:
            mikunu_msg += f'\nResponse error: {response}'
        await mikunu.send(mikunu_msg)
    '''


def setup(client):
    client.add_cog(Report(client))
