from core.commands.base import Command


class Aplication(Command):
    help = "Sends a test email to the email addresses specified as arguments."
    missing_args_message = "You must specify some email recipients, or pass the --managers or --admin options."
    
    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **kwargs):
        pass