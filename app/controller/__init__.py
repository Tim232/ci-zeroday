import logging
import asyncio

from typing import Optional
from threading import Thread

from app.services.discord_core import DiscordClient
from app.services.fastapi_core import Server


class Controller:
    def __init__(
            self,
            token: str,
            prefix: str,
            host: str = "127.0.0.1",
            port: int = 8080,
            title: str = "",
            description: str = "",
            fast_api_debug: bool = False,
            asgi_debug: bool = False,
            discord_debug: bool = False,
            loop=None
    ) -> None:
        self.loop = loop or self._loop()
        self.logging = logging

        # FastAPI Configuration parameters
        self.title = title
        self.description = description
        self.fast_api_debug = fast_api_debug

        # uvicorn configuration parameters
        self.server_host = host
        self.server_port = port
        self.asgi_debug = asgi_debug

        # discord.py configuration parameters
        self.discord_debug = discord_debug
        self.discord_token = token
        self.discord_prefix = prefix

        self.zeroday_client: Optional[DiscordClient] = None
        self.fast_api_server: Optional[Server] = None
        self.th: Optional[Thread] = None
        self.thr = []

    def _loop(self):
        return asyncio.get_event_loop()

    @property
    def logger(self):
        return self.logging.getLogger(f"{self.__class__.__module__}: {self.__class__.__name__}")

    def startup(self) -> None:
        self.fast_api_server = Server(
            ctx=self,
            host=self.server_host,
            port=self.server_port,
            title=self.title,
            description=self.description,
            asgi_debug=self.asgi_debug,
            debug=self.fast_api_debug
        )
        self.zeroday_client = DiscordClient(
            soc=self,
            token=self.discord_token,
            command_prefix=self.discord_prefix,
            case_insensitive=True,
            shard_count=10,
            shard_ids=(1, 2, 5, 6)
        )

        @self.fast_api_server.on_event("startup")
        async def start_up():
            asyncio.ensure_future(self.zeroday_client.start(self.discord_token), loop=self.loop)
            self.th = Thread(target=self.loop.run_forever)
            self.th.start()

    def start(self) -> None:
        self.fast_api_server.make_process()
