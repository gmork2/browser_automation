from email.header import Header
from email.utils import getaddresses, parseaddr

from conf import config
from core.mail.exceptions import BadHeaderError
from utils.encoding import force_text


# Header names that contain structured address data (RFC #5322)
ADDRESS_HEADERS = {
    'from',
    'sender',
    'reply-to',
    'to',
    'cc',
    'bcc',
    'resent-from',
    'resent-sender',
    'resent-to',
    'resent-cc',
    'resent-bcc',
}

def forbid_multi_line_headers(name, val, encoding):
    """Forbids multi-line headers, to prevent header injection."""
    encoding = encoding or config['default_charset']
    val = force_text(val)
    if '\n' in val or '\r' in val:
        raise BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (val, name))
    try:
        val.encode('ascii')
    except UnicodeEncodeError:
        if name.lower() in ADDRESS_HEADERS:
            val = ', '.join(sanitize_address(addr, encoding) for addr in getaddresses((val,)))
        else:
            val = Header(val, encoding).encode()
    else:
        if name.lower() == 'subject':
            val = Header(val).encode()
    return str(name), val

def split_addr(addr, encoding):
    """
    Split the address into local part and domain, properly encoded.

    When non-ascii characters are present in the local part, it must be
    MIME-word encoded. The domain name must be idna-encoded if it contains
    non-ascii characters.
    """
    if '@' in addr:
        localpart, domain = addr.split('@', 1)
        # Try to get the simplest encoding - ascii if possible so that
        # to@example.com doesn't become =?utf-8?q?to?=@example.com. This
        # makes unit testing a bit easier and more readable.
        try:
            localpart.encode('ascii')
        except UnicodeEncodeError:
            localpart = Header(localpart, encoding).encode()
        domain = domain.encode('idna').decode('ascii')
    else:
        localpart = Header(addr, encoding).encode()
        domain = ''
    return (localpart, domain)


def sanitize_address(addr, encoding):
    """
    Format a pair of (name, address) or an email address string.
    """
    if not isinstance(addr, tuple):
        addr = parseaddr(force_text(addr))
    nm, addr = addr
    localpart, domain = None, None
    nm = Header(nm, encoding).encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN or non-ascii in the local part
        localpart, domain = split_addr(addr, encoding)

    # On Python 3, an 'email.headerregistry.Address' object is used since
    # email.utils.formataddr() naively encodes the name as ascii (see #25986).
    from email.headerregistry import Address
    from email.errors import InvalidHeaderDefect, NonASCIILocalPartDefect

    if localpart and domain:
        address = Address(nm, username=localpart, domain=domain)
        return str(address)

    try:
        address = Address(nm, addr_spec=addr)
    except (InvalidHeaderDefect, NonASCIILocalPartDefect):
        localpart, domain = split_addr(addr, encoding)
        address = Address(nm, username=localpart, domain=domain)
    return str(address)