import discord
import os
import sqlite3
from discord.ext import commands
from config import settings


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=settings['prefix'], intents=intents)

conn = sqlite3.connect("pgd.db")
cursor = conn.cursor()


@client.command(brief='Загружает модуль')
@commands.has_role('Админ')
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command(brief='Выгружает модуль')
@commands.has_role('Админ')
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(settings['token'])
