from time import mktime
import discord
from discord.ext import commands
from bot import sql_worker, client
from extensions.useful_funtions import check_if_user_has_projects, grant_channel_roles, is_in_devlogs


class ProjectsAdmin(commands.Cog, description='Админские команды девлогов'):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_any_role('Админ', 'Модератор')
    @commands.check(is_in_devlogs)
    async def devlog(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Слишком мало аргументов')

    @devlog.command(name='create',
                    help='create @user | Создаёт канал разработки для пользователя',
                    brief='Создаёт канал разработки для пользователя')
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
        sql_worker.add_devlog(channel_id=channel.id, user_id=member.id)

        result = sql_worker.get_devlog_by_channel(channel.id)
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
    async def delete_project(self, ctx: discord.ext.commands.Context, silent: str=''):
        devlog = sql_worker.get_devlog_by_channel(ctx.channel.id)
        if devlog is None:
            await ctx.reply(f'Данного проекта нет в базе данных', delete_after=5)
            await ctx.message.delete()
            return

        sql_worker.delete_devlog(devlog)
        message = f'Канал разработки {client.get_channel(devlog.channel_id).name} от ' \
                  f'{client.get_user(devlog.user_id).mention} был удалён {ctx.author.mention}'
        if silent != '-s':
            await discord.utils.get(ctx.guild.channels, id=759775534136819722).send(message)  # аудит
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

    @commands.command(name='assign',
                      help='assign @user | Присваивает канал разработки пользователю',
                      brief='Присваивает канал разработки пользователю',
                      enabled=False)
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


def setup(client):
    client.add_cog(ProjectsAdmin(client))
