#!/usr/bin/env python
import logging
import sys

from conf import settings
from core.commands.base import Command
from utils.loading import import_string


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = import_string(settings.APP)
    if issubclass(app, Command):
        app().run_from_argv(sys.argv)
    sys.exit(0)
