from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction
from discord.app_commands import Group, Range, describe
from discord.ext.commands import Cog

from .utils import (
    TagExists,
    TagNotFound,
    MissingPermissionsForTagDeletion,
    MissingPermissionsForTagEdit,
)


if TYPE_CHECKING:
    from ..bot import Bot


class Tags(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    tags = Group(name="tags", description="Commands for managing tags", guild_only=True)

    @tags.command(name="create", description="Creates a tag")
    @describe(
        name="The name of the tag",
        content="The content of the tag",
    )
    async def create_tag(
        self,
        interaction: Interaction,
        name: Range[str, 1, 32],
        content: Range[str, 1, 2000],
    ):
        existing_tag = await self.bot.tags.find_one(
            {
                "_name": name.lower(),
            }
        )

        if existing_tag:
            raise TagExists

        await self.bot.tags.insert_one(
            {
                "name": name,
                "_name": name.lower(),
                "content": content,
                "author": interaction.user.id,
            }
        )

        await interaction.response.send_message(
            f"Successfully created tag `{name}`",
            ephemeral=True,
        )

    @tags.command(name="delete", description="Deletes a tag")
    @describe(
        name="The name of the tag",
    )
    async def delete_tag(
        self,
        interaction: Interaction,
        name: Range[str, 1, 32],
    ):
        tag = await self.bot.tags.find_one(
            {
                "_name": name.lower(),
            }
        )

        if not tag:
            raise TagNotFound

        if (
            tag["author"] != interaction.user.id
            and not interaction.permissions.manage_messages
        ):
            raise MissingPermissionsForTagDeletion

        await self.bot.tags.delete_one(tag)

        await interaction.response.send_message(
            f"Successfully deleted tag `{name}`",
            ephemeral=True,
        )

    @tags.command(name="edit", description="Edits a tag")
    @describe(
        name="The name of the tag",
        content="The new content of the tag",
    )
    async def edit_tag(
        self,
        interaction: Interaction,
        name: Range[str, 1, 32],
        content: Range[str, 1, 2000],
    ):
        tag = await self.bot.tags.find_one(
            {
                "_name": name.lower(),
            }
        )

        if not tag:
            raise TagNotFound

        if (
            tag["author"] != interaction.user.id
            and not interaction.permissions.manage_messages
        ):
            raise MissingPermissionsForTagEdit

        await self.bot.tags.update_one(
            tag,
            {
                "$set": {
                    "content": content,
                }
            },
        )

        await interaction.response.send_message(
            f"Successfully edited tag `{name}`",
            ephemeral=True,
        )

        # TODO: Maybe an audit log?
        # TODO: Should add aliases?


async def setup(bot: Bot):
    await bot.add_cog(Tags(bot))
