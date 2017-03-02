import os

from core.commands.base import Command
from core.test.builder import Builder
from core.commands.utils import get_runner


class Aplication(Command):
    help = 'Discover and run tasks in the specified modules or the current directory.'

    def __init__(self):
        self.test_runner = None
        super(Aplication, self).__init__()

    def run_from_argv(self, argv):
        """
        Pre-parse the command line to extract the value of the --testrunner
        option. This allows a test runner to define additional command line
        arguments.
        """
        option = '--testrunner='
        for arg in argv[2:]:
            if arg.startswith(option):
                self.test_runner = arg[len(option):]
                break
        super(Aplication, self).run_from_argv(argv)

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='test_label', nargs='*',
            help='Module paths to test; can be modulename, modulename.TestCase or modulename.TestCase.test_method'
        )
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive', default=True,
            help='Tells Browser Automation to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--failfast', action='store_true', dest='failfast', default=False,
            help='Tells Browser Automation to stop running the test suite after first failed test.',
        )
        parser.add_argument(
            '--testrunner', action='store', dest='testrunner',
            help='Tells Browser Automation to use specified test runner class instead of '
                 'the one specified by the TEST_RUNNER setting.',
        )
        parser.add_argument(
            '--liveserver', action='store', dest='liveserver', default=None,
            help='Overrides the default address where the live server (used '
                 'with LiveServerTestCase) is expected to run from. The '
                 'default value is localhost:8081-8179.',
        )

        test_runner_class = get_runner(self.test_runner)

        if hasattr(test_runner_class, 'add_arguments'):
            test_runner_class.add_arguments(parser)

    def handle(self, *test_labels, **options):
        TestRunner = get_runner(options['testrunner'])

        if options['liveserver'] is not None:
            os.environ['BROWSER_AUTOMATION_SERVER_ADDRESS'] = options['liveserver']
        del options['liveserver']
        
        builder = Builder(pattern="do_*.py", test_runner=TestRunner)
        suite, result = builder.run_tests(['tasks'])



