from typing import Any

import discord
from discord.ext import commands

from bot import cursor, conn


def get_data_for_projects(ctx: discord.ext.commands.Context):
    channel_id = ctx.channel.id
    cursor.execute("""select * from projectChannels where channel_id = ?""", (channel_id,))
    return cursor.fetchone()


def check_if_user_has_projects(member: discord.Member):
    sqlite_select_query = """SELECT author_id from projectChannels"""
    cursor.execute(sqlite_select_query)
    authors = cursor.fetchall()
    members = []
    for author in authors:
        members.append(author[0])

    if member.id in members:
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
            await self.check_member_projects(ctx, member)
            return

        channel_name = f'проект {member.name}'
        category = discord.utils.get(ctx.guild.channels, id=715126363748827136)
        topic = 'Канал разработки'
        channel: discord.TextChannel = await ctx.guild.create_text_channel(channel_name, category=category, topic=topic)
        perms = grant_channel_roles(member, channel)
        await channel.set_permissions(member, overwrite=perms)
        await ctx.send(f'{member.name}, {channel.mention} в категории "{category}" создан')

        member_fullname = f'{member.name}#{member.discriminator}'
        data_to_add = (member_fullname, member.id, channel.name, channel.id)
        cursor.execute("""INSERT INTO projectChannels
                          VALUES (?, ?, ?, ?)""", data_to_add)
        conn.commit()

    @commands.command(name='delete-project',
                      help='delete-project | Удаляет канал разработки, в котором команда написана',
                      brief='Удаляет канал разработки в котором команда написана')
    @commands.has_any_role('Админ', 'Модератор')
    async def delete_project(self, ctx: discord.ext.commands.Context):
        project_data = get_data_for_projects(ctx)
        if project_data is None:
            await ctx.reply(f'project data is None', delete_after=3)
            await ctx.message.delete()
            return

        message = f'Канал разработки {project_data[2]} от <@{project_data[1]}> был удалён {ctx.author.mention}'
        await discord.utils.get(ctx.guild.channels, id=759775534136819722).send(message)  # аудит
        sql_delete_query = """DELETE from projectChannels where channel_id = ?"""
        cursor.execute(sql_delete_query, (project_data[3],))
        conn.commit()
        await ctx.channel.delete()

    @commands.command(name='users-projects',
                      help='Недоступная для всех временная команда',
                      brief='Недоступная для всех временная команда')
    @commands.has_any_role('Админ')
    async def users_projects(self, ctx: discord.ext.commands.Context):
        sqlite_select_query = """SELECT author_id from projectChannels"""
        cursor.execute(sqlite_select_query)
        authors = cursor.fetchall()
        members = []
        for author in authors:
            members.append(ctx.guild.get_member(author[0]))
        for member in members:
            print(member)

    @commands.command(name='check-member-projects',
                      help='check-member-projects @user | Вывести проект пользователя',
                      brief='Вывести проект пользователя')
    @commands.has_any_role('Админ', 'Модератор')
    async def check_member_projects(self, ctx: discord.ext.commands.Context, member: discord.Member):
        if check_if_user_has_projects(member):
            sqlite_select_query = """SELECT * from projectChannels where author_id = ?"""
            cursor.execute(sqlite_select_query, (member.id, ))
            print(cursor.description)
            project_data = cursor.fetchone()
            print(project_data)
            await ctx.reply(f'{member.mention} уже имеет проект.\nДанные проекта:\n'
                            f'Владелец: <@{project_data[1]}>\nПроект: <#{project_data[3]}>')
        else:
            await ctx.reply(f'{member.mention} не имеет проекта')

    @commands.command(name='rename-project',
                      help='rename-project название или rename-project "название с пробелами" '
                           '| Переименовывает канал разработки',
                      brief='Переименовывает канал')
    async def rename_project(self, ctx: discord.ext.commands.Context, new_name: str):
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
            await ctx.channel.edit(name=new_name)
            sql_update_query = """Update projectChannels set channel_name = ? where channel_id = ?"""
            data = (new_name, project_data[3])
            cursor.execute(sql_update_query, data)
            conn.commit()
            await ctx.reply(f'<@{project_data[1]}>, ваш канал был переименован в: {new_name}')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @commands.command(name='update-topic', rest_is_raw=True,
                      help='update-topic описание или update-topic "описание с пробелами" '
                           '| Изменить описание канала разработки',
                      brief='Изменить описание канала разработки')
    async def update_topic(self, ctx: discord.ext.commands.Context, new_topic: str):
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
            await ctx.channel.edit(topic=new_topic)
            await ctx.reply(f'<@{project_data[1]}>, описание изменено: {new_topic}')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @commands.command(name='archive',
                      help='archive | Перенести канал разрабокти в архив',
                      brief='Перенести канал разработки в архив')
    async def archivize(self, ctx: discord.ext.commands.Context):
        project_data = get_data_for_projects(ctx)
        category = discord.utils.get(ctx.guild.channels, id=719540678673170524)
        if ctx.author.id == project_data[1]:
            await ctx.channel.edit(category=category)
            await ctx.reply(f'<@{project_data[1]}>, канал заархивирован')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @commands.command(name='delete',
                      help='delete ответом на сообщение или указать количество сообщений (до 99) '
                           '| Удаляет сообщение(я)',
                      brief='Удаляет сообщение(я)')
    async def delete_message(self, ctx: discord.ext.commands.Context, limit: int = None):
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
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
        project_data = get_data_for_projects(ctx)
        if project_data is not None:
            await ctx.reply(f'Данная комната уже закреплена за {project_data[0]}')
            return

        channel: discord.TextChannel = ctx.channel
        perms = grant_channel_roles(member, channel)
        await channel.set_permissions(member, overwrite=perms)

        member_fullname = f'{member.name}#{member.discriminator}'
        data_to_add = (member_fullname, member.id, channel.name, channel.id)
        cursor.execute("""INSERT INTO projectChannels
                          VALUES (?, ?, ?, ?)""", data_to_add)
        conn.commit()
        project_data = get_data_for_projects(ctx)
        await ctx.reply(f'Канал <#{project_data[3]}> закреплён за <@{project_data[1]}>')

    @commands.command(name='unassign',
                      help='unassign | Открепляет комнату от пользователя',
                      brief='Открепляет комнату от пользователя')
    @commands.has_any_role('Админ', 'Модератор')
    async def unassign(self, ctx: discord.ext.commands.Context):
        project_data = get_data_for_projects(ctx)
        if project_data is None:
            await ctx.reply(f'Данная комната ни за кем не закреплена')
            return
        member: discord.Member = ctx.guild.get_member(project_data[0])
        await ctx.channel.set_permissions(member, overwrite=None)
        sql_delete_query = """DELETE from projectChannels where channel_id = ?"""
        cursor.execute(sql_delete_query, (project_data[3],))
        conn.commit()
        await ctx.reply(f'Канал <#{project_data[3]}> больше не закреплён за <@{project_data[1]}>')

    @commands.command(name='projects-update-perms')
    @commands.has_any_role('Админ')
    async def projets_update_perms(self, ctx: discord.ext.commands.Context):
        projects_data = cursor.execute('SELECT author_id, channel_id from projectChannels').fetchall()
        users_updated = len(projects_data)
        for project_data in projects_data:
            try:
                member: discord.User = ctx.guild.get_member(project_data[0])
                channel: discord.TextChannel = ctx.guild.get_channel(project_data[1])
                perms = grant_channel_roles(member, channel)
                await channel.set_permissions(member, overwrite=perms)
            except Exception as e:
                users_updated -= 1
        role: discord.Role = discord.utils.get(ctx.guild.roles, id=917023053890859039)
        await ctx.reply(f'{users_updated} из {len(role.members)} пользователей обновлено')

    @commands.command(name='projects-remove2fa')
    async def projects_remove2fa(self, ctx: discord.ext.commands.Context):
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
            await ctx.channel.set_permissions(ctx.author, overwrite=None)
            await ctx.reply(f'{ctx.author.mention}, '
                            f'ваши права обновлены, теперь для модерации канала пользуйтесь ботом')
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()

    @commands.command(name='projects-get2fa')
    async def projects_get2fa(self, ctx: discord.ext.commands.Context):
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
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
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
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
        project_data = get_data_for_projects(ctx)
        if ctx.author.id == project_data[1]:
            if ctx.message.reference:
                original = await ctx.fetch_message(id=ctx.message.reference.message_id)
                await original.unpin()
                await ctx.message.delete()
        else:
            await ctx.reply(f'{ctx.author.mention}, вы не создатель канала!', delete_after=3)
            await ctx.message.delete()


def setup(client):
    client.add_cog(Projects(client))
