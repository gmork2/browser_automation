class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.
    """
    pass


class SystemCheckError(CommandError):
    """
    The system check framework detected unrecoverable errors.
    """
    pass