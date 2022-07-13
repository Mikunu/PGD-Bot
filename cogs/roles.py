import discord
from discord.ext import commands


class Roles(commands.Cog, description='Команды для управления ролями'):

    @commands.group()
    @commands.has_guild_permissions(manage_roles=True)
    async def role(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @role.command(help='Варианты категорий: gamedev | gd, 3d, 2d, code, other, communities | comms, custom\n'
                       'Пример команды `role create gd PGDEngine',
                  brief='Создание новой роли в определенной категории')
    async def create(self, ctx: commands.Context, *, arg: str):
        category, role_name = arg.split(' ', maxsplit=1)
        category = category.lower()
        if category == 'gd' or category == 'gamedev':
            parent_role_id = 799350135762976791
        elif category == '3d':
            parent_role_id = 799350137045385286
        elif category == '2d':
            parent_role_id = 799351146279600188
        elif category == 'code':
            parent_role_id = 799241398737174528
        elif category == 'other':
            parent_role_id = 799352033337147392
        elif category == 'communities' or category == 'comms':
            parent_role_id = 841965762905374721
        elif category == 'custom':
            parent_role_id = 799349975297425408
        else:
            await ctx.reply('Указана неверная категория')
            return
        parent_role: discord.Role = ctx.guild.get_role(parent_role_id)
        new_role: discord.Role = await ctx.guild.create_role(name=role_name, colour=parent_role.colour, mentionable=True)
        await new_role.edit(position=parent_role.position - 1)
        await ctx.reply(f'Роль **{new_role.mention}** в категории **{parent_role.name}** создана')


def setup(client):
    client.add_cog(Roles(client))
