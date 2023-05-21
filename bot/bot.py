import json
import os

from discord import Intents
from discord.ext.commands import Bot as DBot
from discord.ext.commands import when_mentioned
from motor.motor_asyncio import AsyncIOMotorClient

from .tree import BetterCommandTree

class Bot(DBot):
    def __init__(self):
        intents = Intents()
        intents.guilds = True
        intents.members = True

        super().__init__(
            intents=intents,
            command_prefix=when_mentioned,
            tree_cls=BetterCommandTree,
        )
        self.config = json.load(open("config.json"))
        self.tree: BetterCommandTree
        cluster = AsyncIOMotorClient(self.config["mongo_url"])

        self.tags = cluster["bot"]["tags"]
        self.warns = cluster["bot"]["warns"]

    def reload_config(self):
        with open("config.json") as f:
            self.config = json.load(f)

    async def setup_hook(self) -> None:
        await self.tree.fetch_commands()
        await self.load_extension("jishaku")
        for file_ in os.listdir("./cogs"):
            if file_.endswith(".py"):
                await self.load_extension(f"cogs.{file_[:-3]}")

    def run(self):
        super().run(self.config["token"])
