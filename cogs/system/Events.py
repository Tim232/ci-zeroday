import time
import discord
import datetime

from discord.ext import commands
from discord.ext.commands import Bot


class Events(commands.Cog):
    """Event"""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Discord Presence"""
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                "@zeroday#6204 help \n버그 제보나 건의사항은 여기로  ->: @zeroday0619#0619"
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

        channel = message.channel
        user = message.author
        msg = message.content

        print(f"<{st}>: [{channel}]:[{user}] >> {msg}")


def setup(bot):
    bot.add_cog(Events(bot))
