import discord
from discord.ext import commands
from bot import client


class General(commands.Cog):

    def __init__(self, client):
        self.client = client


@commands.Cog.listener()
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'Missing arguments.\n{error}', delete_after=10)
    # elif isinstance(error, commands.CommandNotFound):
    #     raise error
    elif isinstance(error, commands.DisabledCommand):
        await ctx.reply('Данная команда отключена.', delete_after=10)
    else:
        await ctx.reply(error, delete_after=10)
    await ctx.message.delete()
    raise error

    
def setup(client):
    client.add_cog(General(client))
