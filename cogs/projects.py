from typing import Any
import datetime
import discord
from time import mktime
from discord.ext import commands
from bot import sql_worker, client


def check_if_user_has_projects(member: discord.Member):
    user = sql_worker.get_devlog_by_user(user_id=member.id)
    if user is not None:
        return True
    else:
        return False


def grant_channel_roles(member: discord.Member, channel: discord.TextChannel):
    perms = channel.overwrites_for(member)
    perms.manage_channels = True
    perms.manage_emojis = True
    perms.manage_messages = True
    return perms


class Projects(commands.Cog, description='Команды девлогов'):

    def __init__(self, client):
        self.client = client

    @commands.command(name='create-project',
                      help='create-project @user | Создаёт канал разработки для пользователя',
                      brief='Создаёт канал разработки для пользователя')
    @commands.has_any_role('Админ', 'Модератор')
    async def create_project(self, ctx: discord.ext.commands.Context, member: discord.Member):
        if member is None:
            return

        if check_if_user_has_projects(member):
            await ctx.reply(f'{member.mention} уже имеет проект')
            await self.check_member_projects(ctx, member)
            return

        channel_name = f'проект {member.name}'
        category = discord.utils.get(ctx.guild.channels, id=715126363748827136)
        topic = 'Канал разработки'

        channel: discord.TextChannel = await ctx.guild.create_text_channel(channel_name, category=category, topic=topic)
        perms = grant_channel_roles(member, channel)
        await channel.set_permissions(member, overwrite=perms)
        result = sql_worker.add_devlog(channel_id=channel.id, user_id=member.id)

        if result is None:
            await ctx.reply(f'Что-то произошло не так, свяжитесь с <@302734324648902657>.\n'
                            f'[INFO] Channel: {channel.id}, {channel.name}')
            return

        if sql_worker.get_author(member.id) is None:
            sql_worker.add_author(member.id)
        else:
            sql_worker.increase_devlog_amount(member.id)

        await ctx.reply(f'{member.mention}, {channel.mention} в категории "{category}" создан.\n'
                        f'Уникальный идентификатор девлога: {sql_worker.get_devlog_by_channel(channel.id).devlog_id}')

        with open('resources/devlog_welcome_message.txt', encoding='utf-8') as f:
            welcome_txt = f.read()
        await channel.send(f'Привет, {member.mention}.')
        for text in welcome_txt.split('\n\n'):
            await channel.send(text)

    @commands.command(name='delete-project',
                      help='delete-project | Удаляет канал разработки, в котором команда написана',
                      brief='Удаляет канал разработки в котором команда написана')
    @commands.has_any_role('Админ', 'Модератор')
    async def delete_project(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if devlog is None:
            await ctx.reply(f'Данного проекта нет в базе данных', delete_after=5)
            await ctx.message.delete()
            return

        sql_worker.delete_devlog(devlog)
        message = f'Канал разработки {client.get_channel(devlog.channel_id).name} от ' \
                  f'{client.get_user(devlog.user_id).mention} был удалён {ctx.author.mention}'
        # await discord.utils.get(ctx.guild.channels, id=759775534136819722).send(message)  # аудит
        await client.get_channel(devlog.channel_id).delete()

    @commands.command(name='check-member-projects',
                      help='check-member-projects @user | Вывести проект пользователя',
                      brief='Вывести проект пользователя')
    @commands.has_any_role('Админ', 'Модератор')
    async def check_member_projects(self, ctx: discord.ext.commands.Context, member: discord.Member):
        if check_if_user_has_projects(member):

            devlog = sql_worker.get_devlog_by_user(member.id)
            user: discord.Member = client.get_user(devlog.user_id)
            channel: discord.TextChannel = client.get_channel(devlog.channel_id)
            embed: discord.Embed = discord.Embed(image=user.avatar_url)
            embed.add_field(name=f'Владелец:', value=user.mention)
            embed.add_field(name=f'Проект:', value=channel.mention)
            embed.add_field(
                name=f'В архиве:',
                value=f'{f"C <t:{round(mktime(devlog.archived_date.timetuple()))}:f>" if devlog.archived else "Нет"}')

            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f'{member.mention} не имеет проекта')

    @commands.command(name='rename-project',
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

    @commands.command(name='update-topic', rest_is_raw=True,
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

    @commands.command(name='archive',
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

    @commands.command(name='delete',
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

    @commands.command(name='assign',
                      help='assign @user | Присваивает канал разработки пользователю',
                      brief='Присваивает канал разработки пользователю')
    @commands.has_any_role('Админ', 'Модератор')
    async def assign(self, ctx: discord.ext.commands.Context, member: discord.Member):
        if check_if_user_has_projects(member):
            await ctx.reply(f'{member.mention} уже имеет проект')
            await self.check_member_projects(ctx, member)
            return

        devlog = sql_worker.add_devlog(channel_id=ctx.channel.id, user_id=member.id)

        if devlog is None:
            await ctx.reply(f'Что-то произошло не так, свяжитесь с <@302734324648902657>.\n'
                            f'[INFO] Channel: {ctx.channel.id}, {ctx.channel.name}')
            return

        if sql_worker.get_author(member.id) is None:
            sql_worker.add_author(member.id)
        else:
            sql_worker.increase_devlog_amount(member.id)
        await ctx.reply(f'Канал {client.get_channel(devlog.channel_id).mention} закреплён '
                        f'за {client.get_user(devlog.user_id).mention}', delete_after=7)
        await ctx.message.delete()

    @commands.command(name='projects-remove2fa')
    async def projects_remove2fa(self, ctx: discord.ext.commands.Context):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if ctx.author.id == devlog.devlog_id:
            await ctx.channel.set_permissions(ctx.author, overwrite=None)
            await ctx.reply(f'{ctx.author.mention}, '
                            f'ваши права обновлены, теперь для модерации канала пользуйтесь ботом')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @commands.command(name='projects-get2fa')
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


    @commands.command(name='pin',
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

    @commands.command(name='unpin',
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
    client.add_cog(Projects(client))
