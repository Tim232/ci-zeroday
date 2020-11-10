import logging
from app.controller import Controller
from app.settings import Settings

logging.basicConfig(level=logging.INFO)

conf = Settings.config()

client = Controller(
    token=conf[0].token,
    prefix=conf[0].prefix,
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

if __name__ == '__main__':
    client.zeroday_client.load_extension("cogs.system.Events")
    client.zeroday_client.load_extension("cogs.system.Management")
    client.zeroday_client.load_extension("cogs.music")
    client.start()