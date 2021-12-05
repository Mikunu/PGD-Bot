import discord
from discord.ext import commands
from bot import cursor, conn


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('[INFO] Bot is online')

    # Создание таблицы
    @commands.command(name='create-tables', help='Недоступная для всех временная команда')
    @commands.has_role('Админ')
    async def create_tables(self, ctx):
        cursor.execute("""CREATE TABLE IF NOT EXISTS mutedUsers
                          (username text, userId text,
                           startTime text, endTime text, reason text)
                       """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS projectChannels
                          (author_name text, author_id integer, channel_name text, channel_id integer)
                       """)
        conn.commit()
        await ctx.send('Done')

    @commands.command(name='update-projects', help='Недоступная для всех временная команда')
    @commands.has_role('Админ')
    async def update_projects(self, ctx: discord.ext.commands.Context):
        sqlite_select_query = """SELECT * from projectChannels"""
        cursor.execute(sqlite_select_query)
        project_data = cursor.fetchall()
        print(project_data)
        for i in range(len(project_data)):
            member = ctx.guild.get_member(project_data[i][1])
            channel = ctx.guild.get_channel(project_data[i][3])
            await channel.set_permissions(member, overwrite=None)
        await ctx.reply('Done')


def setup(client):
    client.add_cog(Admin(client))
