from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from discord import AllowedMentions, Interaction
from discord.app_commands import (
    AppCommand,
    AppCommandError,
    BotMissingPermissions,
    CommandNotFound,
    CommandTree,
    MissingAnyRole,
    MissingPermissions,
    MissingRole,
    NoPrivateMessage,
    CommandOnCooldown,
)

from cogs.utils import (
    TagExists,
    TagNotFound,
    MissingPermissionsForTagDeletion,
    MissingPermissionsForTagEdit,
    WarnNotFound,
    MissingGuildUserData,
    BotFailedHierarchy,
    FailedHierarchy,
    CannotPerformActionOnBot,
    CannotPerformActionOnSelf,
    CannotPerformActionOnOwner,
    CannotPerformActionOnMe,
    InvalidDuration,
    DurationTooLong,
    UserNotMuted,
)

if TYPE_CHECKING:
    from .bot import Bot


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
                    "I am missing the following permissions: " ", ".join(
                        error.missing_permissions
                    )
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
                    "You are missing the following permissions: " ", ".join(
                        error.missing_permissions
                    ),
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
        elif isinstance(error, WarnNotFound):
            await interaction.response.send_message(
                "This warn does not exist.",
                ephemeral=True,
            )
        elif isinstance(error, MissingGuildUserData):
            await interaction.response.send_message(
                "The data for your user indicates this has not been used in a server.",
                ephemeral=True,
            )
        elif isinstance(error, BotFailedHierarchy):
            await interaction.response.send_message(
                (
                    f"{error.target} is above me in roles, meaning I can't do that."
                    "Please move me above them in roles and try again."
                ),
                ephemeral=True,
            )
        elif isinstance(error, FailedHierarchy):
            await interaction.response.send_message(
                (
                    f"{error.target} is above you in roles, meaning you can't do that. "
                    f"Make sure that {error.target.top_role} "
                    f"(position {error.target.top_role.position}) "
                    f"is below {error.invoker.top_role} (position"
                    f"{error.invoker.top_role.position}). "
                    "Please move them below you in roles and try again."
                ),
                ephemeral=True,
            )
        elif isinstance(error, CannotPerformActionOnBot):
            await interaction.response.send_message(
                "You cannot perform this action on a bot.",
                ephemeral=True,
            )
        elif isinstance(error, CannotPerformActionOnSelf):
            await interaction.response.send_message(
                "You cannot perform this action on yourself.",
                ephemeral=True,
            )
        elif isinstance(error, CannotPerformActionOnOwner):
            await interaction.response.send_message(
                "You cannot perform this action on the server owner.",
                ephemeral=True,
            )
        elif isinstance(error, CannotPerformActionOnMe):
            await interaction.response.send_message(
                "You cannot perform this action on me.",
                ephemeral=True,
            )
        elif isinstance(error, InvalidDuration):
            await interaction.response.send_message(
                f"{error.duration} is an invalid duration.",
                ephemeral=True,
            )
        elif isinstance(error, DurationTooLong):
            await interaction.response.send_message(
                f"{error.duration} is too long.",
                ephemeral=True,
            )
        elif isinstance(error, UserNotMuted):
            await interaction.response.send_message(
                "This user is not muted.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "An unknown error occurred while running this command."
            )
            raise error
