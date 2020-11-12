import logging
from app.controller import Controller
from app.settings import Settings
from pretty_help import PrettyHelp, Navigation
from discord import Colour
from discord.ext import commands
logging.basicConfig(level=logging.INFO)

conf = Settings.config()


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = [conf[0].prefix]

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return conf[0].prefix

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


client = Controller(
    token=conf[0].token,
    prefix=get_prefix,
    host=conf[1].host,
    port=conf[1].port,
    title=conf[1].title,
    description=conf[1].description,
    fast_api_debug=conf[1].debug,
    asgi_debug=conf[4],
    discord_debug=conf[0].debug
)
client.startup()


@client.fast_api_server.get("/")
async def read_root():
    return {
        "bot_account_name": str(client.zeroday_client.user.name),
        "bot_account_cid": str(client.zeroday_client.user.id),
        "copyright": "Copyright (C) 2020 zeroday0619",
        "LICENSE": "MIT License",
        "VERSION": "3.0-dev"
    }

nav = Navigation()
color = Colour.blurple()

if __name__ == '__main__':
    client.zeroday_client.load_extension("cogs.system.Events")
    client.zeroday_client.load_extension("cogs.system.Management")
    client.zeroday_client.load_extension("cogs.music")
    client.zeroday_client.help_command = PrettyHelp(navigation=nav, color=color, active=30)
    client.start()