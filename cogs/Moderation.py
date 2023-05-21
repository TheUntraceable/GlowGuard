from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, Member
from discord.app_commands import command, describe, checks
from discord.ext.commands import Cog


if TYPE_CHECKING:
    from ..bot import Bot


class Moderation(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


async def setup(bot: Bot):
    await bot.add_cog(Moderation(bot))
