import discord
from itertools import cycle
from discord.ext import commands, tasks
from discord.ext.commands import Bot

status = cycle(
    [
        "!help",
        "버그 제보나 건의사항은",
        "여기로 ->: @zeroday0619#0619"
    ]
)


class Events(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("!help \n버그 제보나 건의사항은 여기로 ->: @zeroday0619#0619"))


def setup(bot):
    bot.add_cog(Events(bot))
