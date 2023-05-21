from discord.app_commands import AppCommandError


class TagNotFound(AppCommandError):
    """Raised when a tag is not found"""


class TagExists(AppCommandError):
    """Raised when a tag already exists"""

class MissingPermissionsForTagDeletion(AppCommandError):
    """Raised when a user is missing permissions to delete a tag"""