from discord.app_commands import AppCommandError


class TagNotFound(AppCommandError):
    """Raised when a tag is not found"""


class TagExists(AppCommandError):
    """Raised when a tag already exists"""