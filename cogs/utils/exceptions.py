from discord.app_commands import AppCommandError


class TagNotFound(AppCommandError):
    """Raised when a tag is not found"""


class TagExists(AppCommandError):
    """Raised when a tag already exists"""


class MissingPermissionsForTagDeletion(AppCommandError):
    """Raised when a user is missing permissions to delete a tag"""


class MissingPermissionsForTagEdit(AppCommandError):
    """Raised when a user is missing permissions to edit a tag"""


class WarnNotFound(AppCommandError):
    """Raised when a warn is not found"""


class FailedHierarchy(AppCommandError):
    """Raised when a user is missing permissions to perform an action on another user"""


class BotFailedHierarchy(AppCommandError):
    """Raised when the bot is missing permissions to perform an action on a user"""
