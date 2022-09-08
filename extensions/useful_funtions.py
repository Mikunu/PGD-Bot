import discord
import discord.ext
from bot import sql_worker


def split_text(text: str, max_length=1800) -> list[str]:
    """
    Split string into list of strings.

    :param text: string to split.
    :param max_length: max length of string element in list.
    :return: list of strings.
    """
    chunks, chunk_size = len(text), len(text) // max_length
    return [text[i:i + chunk_size] for i in range(0, chunks, chunk_size)]


def can_use_tts(ctx: discord.ext.commands.Context) -> bool:
    """
    Check if user can use TTS.

    :param ctx: discord context.
    :return: True if can, False if can't.
    """
    role_disabled_tts: discord.Role = ctx.guild.get_role(995822671608684676)
    return True if role_disabled_tts not in ctx.author.roles else False


def is_in_devlogs(ctx: discord.ext.commands.Context) -> bool:
    """
    Check if channel in devlogs' category.

    :param ctx: discord context.
    :return: True if in devlogs' category, False if not.
    """
    devlog_category = ctx.channel.category
    return True if devlog_category.id == 715126363748827136 else False  # PGD Devlogs Category ID


def check_if_user_has_projects(member: discord.Member) -> bool:
    """
    Check if user has existing projects.

    :param member: guild member.
    :return: True if user has existing projects, False if not.
    """
    user = sql_worker.get_devlog_by_user(user_id=member.id)
    if user is not None:
        return True
    else:
        return False


def check_if_space_in_category_exists(ctx: discord.ext.commands.Context):
    """Check if place in devlogs' category exists.

    :param ctx: command context.

    :return: bool: If exists.
    """
    category: discord.CategoryChannel = ctx.guild.get_channel(715126363748827136)  # Devlog category id
    if len(category.channels) <= 49:
        return True
    else:
        return False

# CHECK RETURN TYPE
def grant_channel_roles(member: discord.Member, channel: discord.TextChannel) -> discord.Permissions:
    """
    Overwrite devlog's author roles for channel controlling.
    Granted roles: manage_emojis, manage_messages.

    :param member: devlog's author
    :param channel: devlog's channel
    :return: overwrited permissions
    """
    perms = channel.overwrites_for(member)
    perms.manage_emojis = True
    perms.manage_messages = True
    return perms
