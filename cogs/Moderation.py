from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from discord import Forbidden, Interaction, Member, Permissions, File
from discord.app_commands import Group, Range, command, describe, checks, NoPrivateMessage
from discord.ext.commands import Cog

from .utils import WarnNotFound, generate_code, Confirm

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
        
        await interaction.response.defer(
            ephemeral=True
        )

        await self.bot.warns.insert_one(
            {
                "user": user.id,
                "reason": reason,
                "moderator": interaction.user.id,
                "warn_id":  generate_code(16)
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
        if not interaction.guild: # Needed to silence Ruff
            raise NoPrivateMessage
    
        await interaction.response.defer(
            ephemeral=True
        )

        deleted = await self.bot.warns.delete_one(
            {
                "user": user.id,
                "warn_id": warn_id
            }
        )

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
        
        await interaction.response.defer(
            ephemeral=True
        )

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
            ]
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
            await interaction.edit_original_response(
                content="Cancelled."
            )

        await self.bot.warns.delete_many(
            {
                "user": user.id
            }
        )

        await interaction.edit_original_response(
            content=f"Cleared all warns for {user.mention}"
        )


async def setup(bot: Bot):
    await bot.add_cog(Moderation(bot))
