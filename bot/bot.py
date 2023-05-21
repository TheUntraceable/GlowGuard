import json
import os

from typing import List, Optional

from discord import AllowedMentions, Intents
from discord.app_commands import (
    AppCommand,
    AppCommandError,
    BotMissingPermissions,
    CommandNotFound,
    CommandOnCooldown,
    CommandTree,
    MissingAnyRole,
    MissingPermissions,
    MissingRole,
    NoPrivateMessage,
)
from discord.ext.commands import Bot as DBot
from discord.ext.commands import when_mentioned
from discord.interactions import Interaction
from motor.motor_asyncio import AsyncIOMotorClient

from cogs.utils import (
    TagExists,
    TagNotFound,
    MissingPermissionsForTagDeletion,
    MissingPermissionsForTagEdit,
)


class BetterCommandTree(CommandTree):
    """A subclass of CommandTree that adds a few extra methods to make
    it easier to work with application commands"""

    def __init__(self, client: "Bot"):
        super().__init__(client)
        self.application_commands: List[AppCommand] = []

    async def sync(self, *args, **kwargs):
        commands = await super().sync(*args, **kwargs)
        self.application_commands = commands
        return commands

    async def get_application_command(self, *, id: int) -> Optional[AppCommand]:
        """Gets an application command by its ID"""
        if not self.application_commands:
            await self.fetch_commands()

        return next(
            (command for command in self.application_commands if command.id == id),
            None,
        )

    async def fetch_commands(self):
        self.application_commands = await super().fetch_commands()
        return self.application_commands

    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        """Handles errors that occur while invoking application commands"""
        if isinstance(error, CommandNotFound):
            await interaction.response.send_message(
                "This command does not exist.",
                ephemeral=True,
            )
        elif isinstance(error, NoPrivateMessage):
            await interaction.response.send_message(
                "This command cannot be used in private messages.",
                ephemeral=True,
            )
        elif isinstance(error, BotMissingPermissions):
            await interaction.response.send_message(
                (
                    "I am missing the following permissions: "
                    ", ".join(error.missing_permissions)
                ),
                ephemeral=True,
            )
        elif isinstance(error, MissingAnyRole):
            roles = [f"<@&{role}>" for role in error.missing_roles]
            await interaction.response.send_message(
                "You are missing the following roles: " ", ".join(roles),
                allowed_mentions=AllowedMentions.none(),
                ephemeral=True,
            )
        elif isinstance(error, MissingRole):
            await interaction.response.send_message(
                f"You are missing the <@&{error.missing_role}> role.",
                ephemeral=True,
                allowed_mentions=AllowedMentions.none(),
            )
        elif isinstance(error, MissingPermissions):
            await interaction.response.send_message(
                (
                    "You are missing the following permissions: "
                    ", ".join(error.missing_permissions),
                )
            )
        elif isinstance(error, CommandOnCooldown):
            await interaction.response.send_message(
                (
                    f"This command is on cooldown. Try again in {error.retry_after:.2f}"
                    "seconds."
                )
            )
        elif isinstance(error, TagNotFound):
            await interaction.response.send_message(
                "This tag does not exist.",
                ephemeral=True,
            )
        elif isinstance(error, TagExists):
            await interaction.response.send_message(
                "This tag already exists.",
                ephemeral=True,
            )
        elif isinstance(error, MissingPermissionsForTagDeletion):
            await interaction.response.send_message(
                "You are missing permissions to delete this tag.",
                ephemeral=True,
            )
        elif isinstance(error, MissingPermissionsForTagEdit):
            await interaction.response.send_message(
                "You are missing permissions to edit this tag.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "An unknown error occurred while running this command."
            )
            raise error


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
