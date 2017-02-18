from io import BytesIO, StringIO
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import (charset as Charset, generator,)

from core.mail.utils import forbid_multi_line_headers


RFC5322_EMAIL_LINE_LENGTH_LIMIT = 998

# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
utf8_charset = Charset.Charset('utf-8')
utf8_charset.body_encoding = None  # Python defaults to BASE64
utf8_charset_qp = Charset.Charset('utf-8')
utf8_charset_qp.body_encoding = Charset.QP

class MIMEMixin():
    def as_string(self, unixfrom=False, linesep='\n'):
        """
        Return the entire formatted message as a string.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.
        """
        fp = StringIO()
        g = generator.Generator(fp, mangle_from_=False)
        g.flatten(self, unixfrom=unixfrom, linesep=linesep)
        return fp.getvalue()


    def as_bytes(self, unixfrom=False, linesep='\n'):
        """
        Return the entire formatted message as bytes.
        Optional `unixfrom' when True, means include the Unix From_ envelope
        header.
        """
        fp = BytesIO()
        g = generator.BytesGenerator(fp, mangle_from_=False)
        g.flatten(self, unixfrom=unixfrom, linesep=linesep)
        return fp.getvalue()


class SafeMIMEMessage(MIMEMixin, MIMEMessage):

    def __setitem__(self, name, val):
        # message/rfc822 attachments must be ASCII
        name, val = forbid_multi_line_headers(name, val, 'ascii')
        MIMEMessage.__setitem__(self, name, val)


class SafeMIMEText(MIMEMixin, MIMEText):

    def __init__(self, _text, _subtype='plain', _charset=None):
        self.encoding = _charset
        if _charset == 'utf-8':
            # Unfortunately, Python < 3.5 doesn't support setting a Charset instance
            # as MIMEText init parameter (http://bugs.python.org/issue16324).
            # We do it manually and trigger re-encoding of the payload.
            MIMEText.__init__(self, _text, _subtype, None)
            del self['Content-Transfer-Encoding']
            has_long_lines = any(len(l) > RFC5322_EMAIL_LINE_LENGTH_LIMIT for l in _text.splitlines())
            # Quoted-Printable encoding has the side effect of shortening long
            # lines, if any (#22561).
            self.set_payload(_text, utf8_charset_qp if has_long_lines else utf8_charset)
            self.replace_header('Content-Type', 'text/%s; charset="%s"' % (_subtype, _charset))
        elif _charset is None:
            # the default value of '_charset' is 'us-ascii' on Python 2
            MIMEText.__init__(self, _text, _subtype)
        else:
            MIMEText.__init__(self, _text, _subtype, _charset)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEText.__setitem__(self, name, val)


class SafeMIMEMultipart(MIMEMixin, MIMEMultipart):

    def __init__(self, _subtype='mixed', boundary=None, _subparts=None, encoding=None, **_params):
        self.encoding = encoding
        MIMEMultipart.__init__(self, _subtype, boundary, _subparts, **_params)

    def __setitem__(self, name, val):
        name, val = forbid_multi_line_headers(name, val, self.encoding)
        MIMEMultipart.__setitem__(self, name, val)