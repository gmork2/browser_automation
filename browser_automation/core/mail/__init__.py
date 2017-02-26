from conf import config
from core.mail.message import EmailMultiAlternatives, EmailMessage
from utils.loading import import_string


def get_connection(backend=None, fail_silently=False, **kwds):
    """
    Load an email backend and return an instance of it.

    If backend is None (default) config['email_backend'] is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    cls = import_string(backend or config['email_backend'])
    return cls(fail_silently=fail_silently, **kwds)

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.
    """
    cls = import_string(config['email_backend'])
    connection = connection or cls(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()

