import asyncio

import discord
from discord.ext import commands
import os
from speechpro.cloud.speech import synthesis
from extensions.useful_funtions import can_use_tts
from bot import client, synthesis_client


class Voice(commands.Cog, description='Команды для голосового чата'):

    SESSION_API = None

    @commands.group(aliases=['v'], enable=False)
    @commands.check(can_use_tts)
    async def voice(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Слишком мало аргументов')

    @voice.command(aliases=['s'])
    async def say(self, ctx: commands.Context, *, arg: str):
        if len(arg) >= 500:
            await ctx.reply('Слишком длинное сообщение. Сообщение должно быть меньше 500 символов')
            return
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        audio = synthesis_client.synthesize(synthesis.enums.Voice.DASHA, synthesis.enums.PlaybackProfile.SPEAKER, arg)
        with open('output.wav', 'wb') as f:
            f.write(audio)
        source = discord.FFmpegPCMAudio(executable=os.environ['PATH_TO_FFMPEG'], source='output.wav')
        player = voice.play(source)

    @voice.command(aliases=['c', 'j'])
    async def connect(self, ctx):
        connected = ctx.author.voice
        if connected:
            await connected.channel.connect()

    @voice.command(aliases=['dc', 'l'])
    async def disconnect(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()


def setup(client):
    client.add_cog(Voice(client))
