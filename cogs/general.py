import discord
from discord.ext import commands


class General(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f'Missing arguments.\n{error}', delete_after=3)
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            await ctx.reply(error, delete_after=3)
        await ctx.message.delete()
        raise error

def setup(client):
    client.add_cog(General(client))
