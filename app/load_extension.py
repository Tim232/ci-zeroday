from app.controller import Controller
from app.controller import DiscordClient
from typing import List


def ReloadExtension(ctx: DiscordClient, log: Controller, _cogs: List[str]):
    for extension in _cogs:
        try:
            ctx.load_extension(extension)
            log.logger.info(f"Successfully reloaded {extension}")
        except extension as ex:
            log.logger.error(f"Failed to reload extension {extension}: {ex}")
