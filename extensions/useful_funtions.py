import discord
import discord.ext


def split_text(text: str, max_length=1800) -> list[str]:
    chunks, chunk_size = len(text), len(text) // max_length
    return [text[i:i + chunk_size] for i in range(0, chunks, chunk_size)]


def can_use_tts(ctx: discord.ext.commands.Context):
    role_disabled_tts: discord.Role = ctx.guild.get_role(995822671608684676)
    return True if role_disabled_tts not in ctx.author.roles else False
