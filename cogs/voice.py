import discord
from discord.ext import commands
import os
from extensions.useful_funtions import can_use_tts
from speechpro.cloud.speech import synthesis
from bot import client

class Voice(commands.Cog, description='Команды для голосового чата'):

    def __init__(self, client):
        self.client = client
        # SESSION_API = None
        self.synth_client = synthesis.SynthesisClient(
            os.environ['SPEECHPRO_EMAIL'], os.environ['SPEECHPRO_DOMAIN_ID'], os.environ['SPEECHPRO_PASSWORD'])
        self.synth_profile = {'voice': synthesis.enums.Voice.DASHA, 'quality': synthesis.enums.PlaybackProfile.SPEAKER}

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

        audio = self.synth_client.synthesize(self.synth_profile.get('voice'), self.synth_profile.get('quality'), arg)
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
