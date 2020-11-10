from discord.ext import commands
from discord.ext.commands import Bot

from run import client
from app.load_extension import ReloadExtension


class Management(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="reload", hidden=True)
    async def cogs_reload(self, ctx: commands.Context, cog: str):
        try:
            ReloadExtension(ctx=client.zeroday_client, log=client, _cogs=[cog])
        except Exception as ex:
            client.logger.error(ex)
            await ctx.send("Reload Error")


def setup(bot):
    bot.add_cog(Management(bot))