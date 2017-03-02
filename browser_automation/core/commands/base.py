"""
Base classes for writing management commands.
"""
import os
import sys

import pytest

from core.commands.exceptions import SystemCheckError
from utils.version import get_version
from conf import config
from core.commands.parser import CommandParser


class Command(object):
    """
    The base class from which all management commands ultimately
    derive.

    Use this class if you want access to all of the mechanisms which
    parse the command-line arguments and work out what code to call in
    response; if you don't need to change any of that behavior,
    consider using one of the subclasses defined in this file.

    If you are interested in overriding/customizing various aspects of
    the command-parsing and -execution behavior, the normal flow works
    as follows:

    1. ``manage.py`` loads the command class
       and calls its ``run_from_argv()`` method.

    2. The ``run_from_argv()`` method calls ``create_parser()`` to get
       an ``ArgumentParser`` for the arguments, parses them, performs
       any environment changes requested by options like
       ``pythonpath``, and then calls the ``execute()`` method,
       passing the parsed arguments.

    3. The ``execute()`` method attempts to carry out the command by
       calling the ``handle()`` method with the parsed arguments; any
       output produced by ``handle()`` will be printed to standard
       output.

    4. If ``handle()`` or ``execute()`` raised any exception (e.g.
       ``CommandError``), ``run_from_argv()`` will  instead print an error
       message to ``stderr``.

    Thus, the ``handle()`` method is typically the starting point for
    subclasses; many built-in commands and command types either place
    all of their logic in ``handle()``, or perform some additional
    parsing work in ``handle()`` and then delegate from it to more
    specialized methods as needed.

    Several attributes affect behavior at various steps along the way:

    ``can_import_settings``
        A boolean indicating whether the command needs to be able to
        import Browser Automation settings; if ``True``, ``execute()`` will verify
        that this is possible before proceeding. Default value is
        ``True``.

    ``help``
        A short description of the command, which will be printed in
        help messages.

    ``requires_system_checks``
        A boolean; if ``True``, entire project will be checked for errors
        prior to executing the command. Default value is ``True``.
    """
    # Metadata about this command.
    help = ''
    
    # Configuration shortcuts that alter various logic.
    requires_system_checks = True
    
    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def get_version(self):
        """
        Return the current version, which should be correct for all built-in
        commands. User-supplied commands can override this method to return
        their own version.
        """
        return get_version()
    
    def create_parser(self, prog_name, subcommand=None):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        parser = CommandParser(self, prog="%s" % (prog_name), description=self.help or None)
        parser.add_argument('--version', action='version', version=self.get_version())
        parser.add_argument(
            '-v', '--verbosity', action='store', dest='verbosity', default=1,
            type=int, choices=[0, 1, 2, 3],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output',
        )
        parser.add_argument(
            '--skipchecks', action='store_true', dest='skip_checks',
            help='Tells Browser Automation to skip all system checks',
        )
        parser.add_argument(
            '--settings',
            help=(
                'The Python path to a settings module, e.g. '
                'If this isn\'t provided, the BROWSER_AUTOMATION_SETTINGS '
                'environment variable will be used.'
            ),
        )
        parser.add_argument(
            '--pythonpath',
            help='A directory to add to the Python path, e.g. "/home/user/myproject".',
        )
        self.add_arguments(parser)
        return parser
    
    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass
    
    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path
        and Browser Automation settings), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr.
        """
        parser = self.create_parser(argv[0])
        options = parser.parse_args(argv[1:])

        cmd_options = vars(options)

        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())

        if options.settings:
            os.environ['BROWSER_AUTOMATION_SETTINGS'] = options.settings
        elif not config.configured: # @UndefinedVariable
            config.configure() # @UndefinedVariable

        if options.pythonpath:
            sys.path.insert(0, options.pythonpath)

        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)
        finally:
            pass
    
    def execute(self, *args, **options):
        """
        Try to execute this command, performing system checks if needed (as
        controlled by the ``requires_system_checks`` attribute, except if
        force-skipped).
        """
        try:
            if self.requires_system_checks and not options.get('skip_checks'):
                has_passed_tests = self.check()

            output = self.handle(*args, **options)
            if output:
                self.stdout.write(output)
        finally:
            pass
        return output

    def _run_pytest_checks(self, **kwargs):
        return bool(pytest.main())

    def check(self, tags=None, display_num_errors=False,
              include_deployment_checks=False, fail_level=40):
        """
        Uses the system check to validate entire Browser Automation project.
        """
        has_passed_tests = self._run_pytest_checks(
            tags=tags,
            display_num_errors=display_num_errors,
            include_deployment_checks=include_deployment_checks,
            fail_level=fail_level
        )
        return has_passed_tests

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError('subclasses of Command must provide a handle() method')

