from __future__ import annotations

from contextlib import suppress
from datetime import timedelta
from typing import TYPE_CHECKING

from discord import Forbidden, Interaction, Member, Permissions, File, User
from discord.app_commands import (
    Group,
    Range,
    command,
    describe,
    checks,
    NoPrivateMessage,
)
from discord.ext.commands import Cog

from .utils import (
    WarnNotFound,
    Confirm,
    FailedHierarchy,
    BotFailedHierarchy,
    MissingGuildUserData,
    CannotPerformActionOnBot,
    CannotPerformActionOnSelf,
    CannotPerformActionOnOwner,
    CannotPerformActionOnMe,
    InvalidDuration,
    DurationTooLong,
    UserNotMuted,
    generate_code,
    format_timedelta,
    format_reason
)

if TYPE_CHECKING:
    from ..bot import Bot


class Moderation(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    warns = Group(
        name="warns",
        description="Commands for managing warns",
        default_permissions=Permissions(
            manage_messages=True,
        ),
        guild_only=True,
    )

    @warns.command(
        name="add",
        description="Adds a warn to a user",
    )
    @describe(
        user="The user to warn",
        reason="The reason for the warn",
    )
    @checks.has_permissions(manage_messages=True)
    async def warns_add(
        self,
        interaction: Interaction,
        user: Member,
        reason: Range[str, 1, 256],
    ):
        if not interaction.guild:  # Needed to silence Ruff
            raise NoPrivateMessage

        await interaction.response.defer(ephemeral=True)

        await self.bot.warns.insert_one(
            {
                "user": user.id,
                "reason": reason,
                "moderator": interaction.user.id,
                "warn_id": generate_code(16),
            }
        )

        with suppress(Forbidden):
            await user.send(
                f"You have been warned in {interaction.guild.name}. Reason: `{reason}`"
            )

        await interaction.edit_original_response(
            content=f"Warned {user.mention} for `{reason}`"
        )

    @warns.command(
        name="remove",
        description="Removes a warn from a user",
    )
    @describe(
        user="The user to remove the warn from",
        warn_id="The ID of the warn to remove",
    )
    @checks.has_permissions(manage_messages=True)
    async def warns_remove(
        self,
        interaction: Interaction,
        user: Member,
        warn_id: str,
    ):
        if not interaction.guild:  # Needed to silence Ruff
            raise NoPrivateMessage

        await interaction.response.defer(ephemeral=True)

        deleted = await self.bot.warns.delete_one({"user": user.id, "warn_id": warn_id})

        if deleted.deleted_count == 0:
            raise WarnNotFound

        await interaction.edit_original_response(
            content=f"Removed warn with ID `{warn_id}` from {user.mention}"
        )

    @warns.command(
        name="list",
        description="Lists all warns for a user",
    )
    @describe(
        user="The user to list the warns for",
    )
    @checks.has_permissions(manage_messages=True)
    async def warns_list(
        self,
        interaction: Interaction,
        user: Member,
    ):
        if not interaction.guild:
            raise NoPrivateMessage

        await interaction.response.defer(ephemeral=True)

        warns = [warn async for warn in self.bot.warns.find({"user": user.id})]

        if not warns:
            return await interaction.edit_original_response(
                content=f"{user.mention} has no warns"
            )

        warns_file_content = "\n".join(
            [
                f"{warn['warn_id']} - {warn['reason']} - <@{warn['moderator']}>"
                for warn in warns
            ]
        )

        await interaction.edit_original_response(
            content=f"Warns for {user.mention}",
            attachments=[
                File(
                    warns_file_content.encode("utf-8"),
                    f"{user.id}_warns.txt",
                )
            ],
        )

    @warns.command(
        name="clear",
        description="Clears all warns for a user",
    )
    @describe(
        user="The user to clear the warns for",
    )
    @checks.has_permissions(manage_messages=True)
    async def warns_clear(
        self,
        interaction: Interaction,
        user: Member,
    ):
        if not interaction.guild:
            raise NoPrivateMessage

        confirm = Confirm()

        await interaction.response.send_message(
            f"Are you sure you want to clear all warns for {user.mention}?",
            view=confirm,
        )

        await confirm.wait()

        if confirm.value is False:
            await interaction.edit_original_response(content="Cancelled.")

        await self.bot.warns.delete_many({"user": user.id})

        await interaction.edit_original_response(
            content=f"Cleared all warns for {user.mention}"
        )

    @command(
        name="mute",
        description="Mutes a user",
    )
    @describe(
        user="The user to mute",
        reason="The reason for the mute",
        days="The days to mute for",
        hours="The hours to mute for",
        minutes="The minutes to mute for",
        seconds="The seconds to mute for",
    )
    @checks.has_permissions(moderate_members=True)
    @checks.bot_has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: Interaction,
        user: Member,
        reason: Range[str, 1, 256],
        days: Range[int, 0, 28] = 0,
        hours: Range[int, 0, 24] = 0,
        minutes: Range[int, 0, 60] = 0,
        seconds: Range[int, 0, 60] = 0,
    ):
        if not interaction.guild:
            raise NoPrivateMessage
        
        if not self.bot.user:  # Needed to silence Ruff
            # Can never be the case because once connected to gateway
            # we get the data, and only then can we get interactions.
            return  

        if isinstance(interaction.user, User):
            raise MissingGuildUserData

        await interaction.response.defer(ephemeral=True)

        if interaction.user.top_role <= user.top_role:
            raise FailedHierarchy(interaction.user, user)
        elif interaction.guild.me.top_role <= user.top_role:
            raise BotFailedHierarchy(user)
        elif user.id == self.bot.user.id:
            raise CannotPerformActionOnMe
        elif user.bot:
            raise CannotPerformActionOnBot
        elif user.id == interaction.user.id:
            raise CannotPerformActionOnSelf
        elif user.id == interaction.guild.owner_id:
            raise CannotPerformActionOnOwner

        duration = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

        if duration.total_seconds() == 0:
            raise InvalidDuration(duration.total_seconds())
        
        if duration.total_seconds() > timedelta(days=28).total_seconds():
            raise DurationTooLong(duration.total_seconds())

        await user.timeout(
            duration,
            reason=format_reason(interaction.user, reason)
        )

        await interaction.edit_original_response(
            content=(
                f"Muted {user.mention} for {format_timedelta(duration)}."
                f"Reason: `{reason}`"
            )
        )

    @command(
        name="unmute",
        description="Unmutes a user",
    )
    @describe(
        user="The user to unmute",
        reason="The reason for the unmute",
    )
    @checks.has_permissions(moderate_members=True)
    @checks.bot_has_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction: Interaction,
        user: Member,
        reason: Range[str, 1, 256],
    ):
        if not interaction.guild:
            raise NoPrivateMessage

        if not interaction.guild:
            raise NoPrivateMessage
        
        if not self.bot.user:  # Needed to silence Ruff
            # Can never be the case because once connected to gateway
            # we get the data, and only then can we get interactions.
            return  

        if isinstance(interaction.user, User):
            raise MissingGuildUserData

        await interaction.response.defer(ephemeral=True)

        if interaction.user.top_role <= user.top_role:
            raise FailedHierarchy(interaction.user, user)
        elif interaction.guild.me.top_role <= user.top_role:
            raise BotFailedHierarchy(user)
        elif user.id == self.bot.user.id:
            raise CannotPerformActionOnMe
        elif user.bot:
            raise CannotPerformActionOnBot
        elif user.id == interaction.user.id:
            raise CannotPerformActionOnSelf
        elif user.id == interaction.guild.owner_id:
            raise CannotPerformActionOnOwner
        elif user.timed_out_until is None:
            raise UserNotMuted(user)
        
        await user.timeout(None, reason=format_reason(interaction.user, reason))

        await interaction.edit_original_response(
            content=f"Unmuted {user.mention}.\nReason: `{reason}`"
        )

async def setup(bot: Bot):
    await bot.add_cog(Moderation(bot))
