import discord
from discord.ext import commands
from bot import cursor, conn
import csv

class Admin(commands.Cog, description='Админские команды'):

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
        await ctx.reply('Done')

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

    @commands.command(name='gather-db')
    @commands.has_role('Админ')
    async def gather_db(self, ctx):
        cursor.execute('SELECT author_id, channel_id FROM projectChannels')
        project_data = cursor.fetchall()
        with open('output.csv', 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(project_data)
        file = discord.File('output.csv')
        await ctx.send(file=file)

def setup(client):
    client.add_cog(Admin(client))
