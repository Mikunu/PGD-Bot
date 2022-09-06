from typing import Any
import datetime
import discord
from discord.ext import commands
from bot import sql_worker, client
from extensions.useful_funtions import grant_channel_roles, is_in_devlogs


class ProjectsUser(commands.Cog, description='Команды девлогов'):

    def __init__(self, client):
        self.client = client

    @commands.group()
    @commands.check(is_in_devlogs)
    async def dev(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Слишком мало аргументов')

    @dev.command(name='rename-project',
                 help='rename-project название или rename-project "название с пробелами" '
                      '| Переименовывает канал разработки',
                 brief='Переименовывает канал')
    async def rename_project(self, ctx: discord.ext.commands.Context, new_name: str):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            await ctx.channel.edit(name=new_name)
            await ctx.reply(f'{ctx.author.mention}, ваш канал был переименован в: {new_name}', delete_after=7)
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=7)
        await ctx.message.delete()

    @dev.command(name='update-topic', rest_is_raw=True,
                 help='update-topic описание или update-topic "описание с пробелами" '
                      '| Изменить описание канала разработки',
                 brief='Изменить описание канала разработки')
    async def update_topic(self, ctx: discord.ext.commands.Context, new_topic: str):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            await ctx.channel.edit(topic=new_topic)
            await ctx.reply(f'<@{ctx.author.mention}>, описание изменено: {new_topic}', delete_after=7)
            await ctx.message.delete()
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=7)
            await ctx.message.delete()

    @dev.command(name='archive',
                 help='archive | Перенести канал разрабокти в архив',
                 brief='Перенести канал разработки в архив')
    async def archivize(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        category = discord.utils.get(ctx.guild.channels, id=719540678673170524)
        role_admin = ctx.guild.get_role(role_id=712188168199209012)
        role_moder = ctx.guild.get_role(role_id=712189049422741565)

        is_author_has_perms = True if role_admin in ctx.author.roles else \
            True if role_moder in ctx.author.roles else False

        if ctx.author.id == devlog.user_id or is_author_has_perms:
            data_for_update = {'user_id': devlog.user_id, 'archived': True, 'archived_date': datetime.datetime.now()}
            sql_worker.update_devlog(devlog.channel_id, data_for_update)
            await ctx.channel.edit(category=category)
            await ctx.reply(f'{client.get_channel(devlog.channel_id)}, канал заархивирован')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @dev.command(name='delete',
                 help='delete ответом на сообщение или указать количество сообщений (до 99) '
                      '| Удаляет сообщение(я)',
                 brief='Удаляет сообщение(я)')
    async def delete_message(self, ctx: discord.ext.commands.Context, limit: int = None):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            if ctx.message.reference:
                original = await ctx.fetch_message(id=ctx.message.reference.message_id)
                await original.delete()
                await ctx.message.delete()
                await ctx.reply('Сообщение удалено', delete_after=3)
            else:
                if limit is None:
                    await ctx.reply('Укажите количество сообщений для удалений')
                    return
                if limit > 100:
                    await ctx.reply('Количество сообщений для удаления не должно превышать 99')
                    return
                if limit <= 0:
                    await ctx.reply('Количество сообщений для удаления должно превышать 0')
                    return
                channel = ctx.channel
                deleted = await channel.purge(limit=limit + 1)
                await channel.send(f'Удалено {len(deleted) - 1} сообщений', delete_after=3)
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @dev.command(name='projects-remove2fa')
    async def projects_remove2fa(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            await ctx.channel.set_permissions(ctx.author, overwrite=None)
            await ctx.reply(f'{ctx.author.mention}, '
                            f'ваши права обновлены, теперь для модерации канала пользуйтесь ботом')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @dev.command(name='projects-get2fa')
    async def projects_get2fa(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            perms = grant_channel_roles(ctx.author, ctx.channel)
            await ctx.channel.set_permissions(ctx.author, overwrite=perms)
            await ctx.reply(f'{ctx.author.mention}, '
                            f'ваши права обновлены, '
                            f'теперь для модерации канала можете пользоваться как ботом, так и вашими правами')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @dev.command(name='pin',
                 help='pin ответом на сообщение '
                      '| Прикрепляет сообщение',
                 brief='Прикрепляет сообщение')
    async def pin_message(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            if ctx.message.reference:
                original = await ctx.fetch_message(id=ctx.message.reference.message_id)
                await original.pin()
                await ctx.message.delete()
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @dev.command(name='unpin',
                 help='unpin ответом на сообщение '
                      '| Открепляет сообщение',
                 brief='Открепляет сообщение')
    async def unpin_message(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            if ctx.message.reference:
                original = await ctx.fetch_message(id=ctx.message.reference.message_id)
                await original.unpin()
                await ctx.message.delete()
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()


def setup(client):
    client.add_cog(ProjectsUser(client))
