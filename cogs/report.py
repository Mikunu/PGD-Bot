import os
import requests
import discord
from discord.ext import commands
from bot import client
from trello import TrelloClient


class Report(commands.Cog, description='Команды багов и TODO'):

    def __init__(self, client):
        self.client = client
        self.url_cards = "https://api.trello.com/1/cards/"

    @commands.group(aliases=['r'], enable=False)
    async def report(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @report.command()
    async def bug(self, ctx, *, arg):
        headers = {
            "Accept": "application/json"
        }
        author = f'{ctx.author.name}#{ctx.author.discriminator}'
        message_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}'
        description = f'Author: {author}\nIn channel: {ctx.channel}\nMessage link: {message_link}'
        querystring = {"key": os.environ['TRELLO_KEY'],
                       "token": os.environ['TRELLO_TOKEN'],
                       "name": arg,
                       "desc": description,
                       "idList": "61ad2829f7648772697e55e9"
                       }
        mikunu: discord.User = client.get_user(302734324648902657)

        mikunu_msg = f'New bug-report:\nAuthor: {author}\n' \
                     f'In channel: {ctx.channel}\nMessage link: {message_link}\n{arg}'
        response = requests.post(self.url_cards, headers=headers, params=querystring)
        await ctx.message.add_reaction('✅')
        if response.status_code != 200:
            mikunu_msg += f'\nResponse error: {response.status_code, response.content}'
        await mikunu.send(mikunu_msg)

    @report.command()
    async def todo(self, ctx, *, arg):
        headers = {"Accept": "application/json"}
        author = f'{ctx.author.name}#{ctx.author.discriminator}'
        message_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}'
        description = f'Author: {author}\nIn channel: {ctx.channel}\nMessage link: {message_link}'

        querystring = {"key": os.environ['TRELLO_KEY'],
                       "token": os.environ['TRELLO_TOKEN'],
                       "name": arg,
                       "desc": description,
                       "idList": "62cb328284679c341fdfc636"
                       }

        mikunu: discord.User = client.get_user(302734324648902657)
        mikunu_msg = f'New TODO:\nAuthor: {author}\nMessage link: {message_link}\n{arg}'
        response = requests.post(self.url_cards, headers=headers, params=querystring)

        await ctx.message.add_reaction('✅')
        if response.status_code != 200:
            mikunu_msg += f'\nResponse error: {response.status_code, response.content}'
        await mikunu.send(mikunu_msg)

def setup(client):
    client.add_cog(Report(client))
