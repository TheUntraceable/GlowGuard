from discord import Member
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


class BaseFailedHierarchy(AppCommandError):
    """Base exception for hierarchy errors"""

    def __init__(
        self,
        target: Member,
    ):
        self.target = target


class FailedHierarchy(BaseFailedHierarchy):
    def __init__(
        self,
        invoker: Member,
        target: Member,
    ):
        super().__init__(target)
        self.invoker = invoker

    """Raised when a user is missing permissions to perform an action on another user"""


class BotFailedHierarchy(BaseFailedHierarchy):
    """Raised when the bot is missing permissions to perform an action on a user"""


class MissingGuildUserData(AppCommandError):
    """Raised when we receive an instance of User instead of Member"""


class CannotPerformActionOnBot(AppCommandError):
    """Raised when a user attempts to perform a moderation action on the bot"""


class CannotPerformActionOnSelf(AppCommandError):
    """Raised when a user attempts to perform a moderation action on themselves"""


class CannotPerformActionOnOwner(AppCommandError):
    """Raised when a user attempts to perform a moderation action on the owner"""


class CannotPerformActionOnMe(AppCommandError):
    """Raised when a user attempts to perform a moderation action on me"""


class BaseDurationError(AppCommandError):
    """Base exception for duration errors"""

    def __init__(self, duration: float):
        self.duration = duration


class InvalidDuration(BaseDurationError):
    """Raised when a duration is invalid"""


class DurationTooLong(BaseDurationError):
    """Raised when a duration is too long"""

class UserNotMuted(AppCommandError):
    """Raised when a user is not muted"""
    def __init__(self, member: Member):
        self.member = member