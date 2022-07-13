import discord
from discord.ext import commands
from bot import client


class Checker(commands.Cog, description='Команды для различных проверок'):

    @commands.group(aliases=['f'])
    async def checker(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @checker.command(aliases=['perms'])
    async def permission(self, ctx: commands.Context, *, arg: str):
        roles = ctx.guild.roles
        can_everyone = []
        for role in roles:
            perms: discord.Permissions = role.permissions
            if perms.mention_everyone:
                can_everyone.append(role.name)
        await ctx.reply(', '.join(can_everyone))


def setup(client):
    client.add_cog(Checker(client))