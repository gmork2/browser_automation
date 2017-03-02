from core.commands.base import Command


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
        super(Aplication, self).run_from_argv(argv)
    
    def add_arguments(self, parser):
        pass
    
    def handle(self, *test_labels, **options):
        pass

