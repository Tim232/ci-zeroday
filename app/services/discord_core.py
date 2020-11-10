from discord.ext.commands import AutoShardedBot


class DiscordClient(AutoShardedBot):
    def __init__(self, soc, *args, **kwargs):
        self.controller = soc
        self.logger = self.controller.logger

        super().__init__(*args, **kwargs)
