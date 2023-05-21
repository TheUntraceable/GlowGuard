from datetime import timedelta
from random import sample
from string import ascii_letters, digits

from discord import ButtonStyle, Interaction
from discord.ui import View, button


def generate_code(length: int) -> str:
    """Generate a random code with the given length."""
    return "".join(sample(ascii_letters + digits, length))


def format_timedelta(delta: timedelta) -> str:
    """Format a timedelta object into a string."""
    days_string = f"{delta.days} days" if delta.days else ""
    hours_string = f"{delta.seconds // 3600} hours" if delta.seconds // 3600 else ""
    minutes_string = (
        f"{delta.seconds // 60 % 60} minutes" if delta.seconds // 60 % 60 else ""
    )
    seconds_string = f"{delta.seconds % 60} seconds" if delta.seconds % 60 else ""

    return " ".join(
        filter(
            None,
            (
                days_string,
                hours_string,
                minutes_string,
                seconds_string,
            ),
        )
    )


class Confirm(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Yes", style=ButtonStyle.green)
    async def yes(self, interaction: Interaction, _):
        for child in self.children:
            child.disabled = True  # type: ignore
        await interaction.response.edit_message(view=self)

        self.value = True
        self.stop()

    @button(label="No", style=ButtonStyle.red)
    async def no(self, interaction: Interaction, _):
        for child in self.children:
            child.disabled = True  # type: ignore
        await interaction.response.edit_message(view=self)

        self.value = False
        self.stop()
