import os
import ujson
from typing import List, Union
from app.interface.config import discordConfigModel
from app.interface.config import fastapiConfigModel
from app.interface.config import MusicExtensionConfigModel
from app.interface.config import MongoDBConfigModel


class Settings:
    @classmethod
    def is_docker(cls) -> bool:
        return "DOCKER_ZERODAY_BOT_CONFIG" in os.environ

    @classmethod
    def load_docker_config(cls) -> dict:
        load_config = ujson.loads(os.environ["DOCKER_ZERODAY_BOT_CONFIG"])
        return load_config

    @classmethod
    def load_json_file(cls) -> dict:
        with open("config.json", "r") as config_file:
            load_config = ujson.load(config_file)
        config_file.close()
        return load_config

    @classmethod
    def config(cls) -> List[Union[discordConfigModel, fastapiConfigModel, MusicExtensionConfigModel, MongoDBConfigModel, bool]]:
        """Get ZERODAY Bot config \n
        ==============================
        - **discord**: \n
        >>> Settings.config()[0]
        \n
        - **fastapi**: \n
        >>> Settings.config()[1]
        \n
        - **music**: \n
        >>> Settings.config()[2]
        \n
        - **mongodb**: \n
        >>> Settings.config()[3]
        \n
        - **asgi_debug**: \n
        >>> Settings.config()[4]

        --------------------------------
        :return: [discord, fastapi, music, mongodb, asgi_debug]
        """

        zeroday_bot_config = {}

        if os.path.isfile("config.json"):
            if "zeroday_bot_config" in cls.load_json_file():
                zeroday_bot_config = cls.load_json_file()["zeroday_bot_config"]

        if cls.is_docker():
            if "zeroday_bot_config" in cls.load_docker_config():
                zeroday_bot_config = cls.load_docker_config()["zeroday_bot_config"]

        discord = zeroday_bot_config["discord"]
        fastapi = zeroday_bot_config["fastapi"]
        music = zeroday_bot_config['music']
        mongodb = zeroday_bot_config['mongodb']
        asgi_debug: bool = zeroday_bot_config["asgi_debug"]
        conf = [
            discordConfigModel(**discord),
            fastapiConfigModel(**fastapi),
            MusicExtensionConfigModel(**music),
            MongoDBConfigModel(**mongodb),
            asgi_debug
        ]
        return conf