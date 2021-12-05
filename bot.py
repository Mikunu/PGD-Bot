import contextlib
import datetime
import discord
import os
import sqlite3
from discord.ext import commands
from config import settings


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=os.environ['PREFIX'], intents=intents)

conn = sqlite3.connect("pgd.db")
cursor = conn.cursor()


@client.command(brief='Загружает модуль')
@commands.has_role('Админ')
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command(brief='Выгружает модуль')
@commands.has_role('Админ')
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command(brief='Перезагружает модуль')
@commands.has_role('Админ')
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


class HelpEmbed(discord.Embed):  # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Используйте [command] или [category] для большей информации | <> необходимо | [] опционально"
        self.set_footer(text=text)
        self.color = discord.Color.blurple()


class MyHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(  # create our class with some aliases and cooldown
            command_attrs={
                "help": "The help command for the bot",
                "cooldown": commands.Cooldown(1, 3.0, commands.BucketType.user),
                "aliases": ['commands']
            }
        )

    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        """triggers when a `<prefix>help` is called"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.avatar_url)
        usable = 0

        for cog, commands in mapping.items():  # iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands):
                # if no commands are usable in this category, we don't want to display it
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog:  # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "Нет описания"
                else:
                    name = "Вне категорий"
                    description = "Команды вне категорий"

                embed.add_field(name=f"{name} Категория [{amount_commands}]", value=description)

        embed.description = f"{len(client.commands)} команд | {usable} можно использовать"

        await self.send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        signature = self.get_command_signature(
            command)  # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(title=signature, description=command.help or "No help found...")

        if cog := command.cog:
            embed.add_field(name="Категория", value=cog.qualified_name)

        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"

        embed.add_field(name="Можно использовать", value=can_run)

        if command._buckets and (
        cooldown := command._buckets._cooldown):  # use of internals to get the cooldown of the command
            embed.add_field(
                name="Кулдаун",
                value=f"{cooldown.rate} в {cooldown.per:.0f} секунду",
            )

        await self.send(embed=embed)

    async def send_help_embed(self, title, description, commands):  # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "Нет описания...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "Нет описания...")

        await self.send(embed=embed)

    async def send_group_help(self, group):
        """triggers when a `<prefix>help <group>` is called"""
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        """triggers when a `<prefix>help <cog>` is called"""
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title} Категория', cog.description, cog.get_commands())


client.help_command = MyHelp()

client.run(os.environ['TOKEN'])
