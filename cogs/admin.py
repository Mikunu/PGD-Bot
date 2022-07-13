import discord
from discord.ext import commands
import csv


class Admin(commands.Cog, description='Админские команды'):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('[INFO] Bot is online')


def setup(client):
    client.add_cog(Admin(client))
