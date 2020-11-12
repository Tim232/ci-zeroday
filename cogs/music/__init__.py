import traceback
import itertools
import asyncio
import discord
import sys
import re

from validator_collection import checkers
from discord.ext import commands
from discord.ext.commands import (
    Bot, Cog, NoPrivateMessage
)
from app.ext.music.option import (
    EmbedSaftySearch,
    adult_filter,
    embed_ERROR,
    embed_queued,
    embed_value,
    InvalidVoiceChannel,
    VoiceConnectionError,
)
from app.ext.music.YTDLSource import YTDLSource
from app.ext.music.player import Player


class YTDLError(Exception):
    pass


def cleanText(readData):
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', readData)
    return text


class music(Cog):
    """Music Extension / Powered by Safety Search"""

    __slots__ = ("bot", "players")

    def __init__(self, bot: Bot):
        self.bot = bot
        self.players = {}
        self.buildVer = "3.1"
        self.verstring = "Ver"

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError as e:
            print(f"{e.__class__.__module__}: {e.__class__.__name__}")

        try:
            for source in self.players[guild.id].queue._queue:
                source.cleanup()
        except KeyError as e:
            print(f"{e.__class__.__module__}: {e.__class__.__name__}")

        try:
            del self.players[guild.id]
        except KeyError as e:
            print(f"{e.__class__.__module__}: {e.__class__.__name__}")

    @staticmethod
    async def __local_check(ctx):
        if not ctx.guild:
            raise NoPrivateMessage
        return True

    @staticmethod
    async def __error(ctx, error):
        if isinstance(error, NoPrivateMessage):
            try:
                return await ctx.send("이 Command 는 DM 에서 사용할 수 없습니다")
            except discord.HTTPException as e:
                print(f"{e.__class__.__module__}: {e.__class__.__name__}")

        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(
                "Voice Channel 연결중 Error 가 발생하였습니다\n 자신이 Voice Channel에 접속되어 있는 지 확인 바랍니다."
            )

        print("Ignoring exception in command {}".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    def get_player(self, ctx):
        """
        :rtype: object
        """
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    @commands.command(name="connect", aliases=["join"])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """보이스 채널에 들어갑니다"""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError as r2:
                await ctx.send("'Voice channel'에 연결하지 못하였습니다.\n 유효한 'Voice channel'에 자신이 들어와 있는지 확인바랍니다.")
                raise InvalidVoiceChannel(f"{r2.__class__.__module__}: {r2.__class__.__name__}")

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError as TError:
                await ctx.send(f"Moving to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(f"{TError.__class__.__module__}: {TError.__class__.__name__}")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError as TError2:
                await ctx.send(f"Connecting to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(f"{TError2.__class__.__module__}: {TError2.__class__.__name__}")

        await ctx.send(
            "```css\nConnected to **{}**\n```".format(str(channel)), delete_after=10
        )

    @commands.command(name="loop")
    async def _loop(self, ctx, mode: str):
        """반복 재생"""

        player = self.get_player(ctx)

        if not player:
            return

        modes = ["current", "all", "disable"]
        if not mode in modes:
            return await ctx.send(
                f"invalid arg: {mode}\nuse: {'/'.join(modes)}", delete_after=5
            )

        if mode == "disable":
            player.repeat = None
        else:
            player.repeat = mode
        await ctx.send(f"Player repeat: **{mode}**", delete_after=5)

    @commands.command(name="play", aliases=["p"])
    async def play_(self, ctx, *, search: str):
        """Play Music & add Music"""
        await ctx.trigger_typing()

        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)
        player = self.get_player(ctx)
        if checkers.is_url(search):
            source = await YTDLSource.Search(ctx, search, download=False, loop=ctx.bot.loop)
        else:
            search_text = search
            serc = search_text.replace(":", "")
            source = await YTDLSource.Search(ctx, serc, download=False, loop=ctx.bot.loop)

        if await adult_filter(search=source.title, loop=ctx.bot.loop) == 1:
            embed_two = EmbedSaftySearch(data=str(search))
            await ctx.send(embed=embed_two)
            await self.cleanup(ctx.guild)
        else:
            await player.queue.put(source)

    @commands.command(name="playlist", aliases=["pls"])
    async def create_playlist_play(self, ctx: commands.Context, *, search: str):
        """add Youtube Playlist & Play"""
        await ctx.trigger_typing()

        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)

        if await adult_filter(search=search, loop=ctx.bot.loop) == 1:
            embed_two = EmbedSaftySearch(data=str(search))
            await ctx.send(embed=embed_two)
        else:
            player = self.get_player(ctx)
            source = await YTDLSource.create_playlist(ctx, search, download=False, loop=ctx.bot.loop)
            for ix in source:
                await player.queue.put(ix)

    @commands.command(name="search")
    async def _search(self, ctx: commands.Context, *, search: str):
        async with ctx.typing():
            try:
                if checkers.is_url(search):
                    source = await YTDLSource.search_source(ctx, search, download=False, loop=ctx.bot.loop)
                else:
                    sr = search
                    sear = sr.replace(":", "")
                    source = await YTDLSource.search_source(ctx, sear, download=False, loop=ctx.bot.loop)

            except YTDLError as e:
                await ctx.send(f"ERROR: {str(e)}")
            else:
                if source == "sel_invalid":
                    await ctx.send("Invalid selection")
                elif source == "cancel":
                    await ctx.send("cancel")
                elif source == "timeout":
                    await ctx.send("Timeout")
                else:
                    if await adult_filter(search=search, loop=ctx.bot.loop) == 1:
                        embed_two = EmbedSaftySearch(data=str(search))
                        await ctx.send(embed=embed_two)
                    else:
                        vc = ctx.voice_client
                        if not vc:
                            await ctx.invoke(self.connect_)
                        player = self.get_player(ctx)
                        await player.queue.put(source)

    @commands.command(name="pause")
    async def pause_(self, ctx):
        """일시중지"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send(embed=embed_ERROR, delete_after=20)
        elif vc.is_paused():
            return
        embed_pause = discord.Embed(
            title="Music",
            description=f"```css\n{ctx.author} : 일시중지.\n```",
            color=discord.Color.blurple(),
        ).add_field(name=self.verstring, value=self.buildVer)

        vc.pause()
        await ctx.send(embed=embed_pause, delete_after=5)

    @commands.command(name="resume", aliases=["replay", "re"])
    async def resume_(self, ctx):
        """다시 재생"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        embed_resume = discord.Embed(
            title="Music",
            description=f"```css\n**{ctx.author}** : 다시재생.\n```",
            color=discord.Color.blurple(),
        ).add_field(name=self.verstring, value=self.buildVer)

        await ctx.send(embed_resume, delete_after=5)

    @commands.command(name="skip")
    async def skip_(self, ctx):
        """스킵"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f"```css\n{ctx.author} : 스킵!.\n```", delete_after=5)

    @commands.command(name="remove", aliases=["rm"])
    async def _remove(self, ctx, index: int):
        player = self.get_player(ctx)
        if len(player.queue._queue) == 0:
            return await ctx.send("Empty queue", delete_after=10)

        player.queue.remove(index - 1)
        await ctx.send("Success delete song", delete_after=10)

    @commands.command(name="shuffle", aliases=["sff"])
    async def _shuffle(self, ctx):
        player = self.get_player(ctx)
        if len(player.queue._queue) == 0:
            return await ctx.send("Empty queue", delete_after=10)

        player.queue.shuffle()
        await ctx.send("Success")

    @commands.command(name="queue", aliases=["q"])
    async def queue_info(self, ctx):
        """재생목록"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send(embed=embed_queued)

        upcoming = list(itertools.islice(player.queue._queue, 0, 50))
        fmt = "\n".join(f'```css\n{_["title"]}\n```' for _ in upcoming)
        embed_queue = discord.Embed(
            title=f"Upcoming - Next **{len(upcoming)}**",
            description=fmt,
            color=discord.Color.blurple(),
        ).add_field(name=self.verstring, value=self.buildVer)

        await ctx.send(embed=embed_queue)

    @commands.command(
        name="now_playing", aliases=["np", "current"]
    )
    async def now_playing_(self, ctx):
        """재생중인 컨텐츠 정보 보기"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send(embed=embed_ERROR)

        try:
            await player.np.delete()
        except discord.HTTPException:
            pass
        embed_now_playing = discord.Embed(
            title=f"Now Playing: ```{vc.source.title}```",
            description=f"requested by @{vc.source.requester}",
            color=discord.Color.blurple(),
        ).add_field(name=self.verstring, value=self.buildVer)
        player.np = await ctx.send(embed=embed_now_playing)

    @commands.command(name="volume", aliases=["vol"])
    async def change_volume(self, ctx, *, vol: float):
        """사운드 크기 조절"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=10)

        if not 0 < vol < 101:
            return await ctx.send(embed_value)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed_now_playing = discord.Embed(
            title="Music",
            description=f"```{ctx.author}: Set the volume to {vol}%```",
            color=discord.Color.blurple(),
        ).add_field(name=self.verstring, value=self.buildVer)

        await ctx.send(embed=embed_now_playing, delete_after=10)

    @commands.command(name="stop")
    async def stop_(self, ctx):
        """stop"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=embed_ERROR, delete_after=20)

        await self.cleanup(ctx.guild)


def setup(bot: Bot):
    bot.add_cog(music(bot))
