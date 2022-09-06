import discord
import os
# from extensions.db_worker import SQLWorker
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
activity = discord.Activity(name='Азимова', type=discord.ActivityType.listening)
client = commands.Bot(command_prefix=os.environ['PREFIX'], intents=intents, activity=activity)
sql_worker = None # SQLWorker()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.environ['DISCORD_BOT_TOKEN'])
