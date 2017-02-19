import logging
import mimetypes
import os
from email import (encoders as Encoders, message_from_string,)
from email.message import Message
from email.mime.base import MIMEBase
from email.utils import formatdate

from conf import config
from core.mail.mime import SafeMIMEMessage, SafeMIMEText, SafeMIMEMultipart
from utils.encoding import force_text
from core.mail.utils import make_msgid, DNS_NAME

logger = logging.getLogger(__name__)

# Default MIME type to use on attachments (if it is not explicitly given
# and cannot be guessed).
DEFAULT_ATTACHMENT_MIME_TYPE = 'application/octet-stream'


class EmailMessage(object):
    """
    A container for email information.
    """
    content_subtype = 'plain'
    mixed_subtype = 'mixed'
    encoding = None     # None => use conf default

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, cc=None,
                 reply_to=None):
        """
        Initialize a single email message (which can be sent to multiple
        recipients).

        All strings used to create the message can be unicode strings
        (or UTF-8 bytestrings). The SafeMIMEText class will handle any
        necessary encoding conversions.
        """

        self.to = list(to) if to else []
        self.cc = list(cc) if to else []
        self.bcc = list(bcc) if bcc else []
        self.reply_to = list(reply_to) if reply_to else []
        self.from_email = from_email or config['default_from_email']
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.extra_headers = headers or {}
        self.connection = connection

    def get_connection(self, fail_silently=False):
        if not self.connection:
            from utils.loading import import_string
            cls = import_string(config['email_backend'])
            self.connection = cls(fail_silently=fail_silently)
        return self.connection

    def message(self):
        encoding = self.encoding or config['default_charset']
        msg = SafeMIMEText(self.body, self.content_subtype, encoding)
        msg = self._create_message(msg)
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_email)
        msg['To'] = self.extra_headers.get('To', ', '.join(map(force_text, self.to)))
        if self.cc:
            msg['Cc'] = ', '.join(map(force_text, self.cc))
        if self.reply_to:
            msg['Reply-To'] = self.extra_headers.get('Reply-To', ', '.join(map(force_text, self.reply_to)))

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            # Use cached DNS_NAME for performance
            msg['Message-ID'] = make_msgid(domain=DNS_NAME)
        for name, value in self.extra_headers.items():
            if name.lower() in ('from', 'to'):  # From and To are already handled
                continue
            msg[name] = value
        return msg

    def recipients(self):
        """
        Returns a list of all recipients of the email (includes direct
        addressees as well as Cc and Bcc entries).
        """
        return self.to + self.cc + self.bcc

    def send(self, fail_silently=False):
        """
        Sends the email message.
        """
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to
            # send to.
            return 0
        return self.get_connection(fail_silently).send_messages([self])

    def attach(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content is None
            assert mimetype is None
            self.attachments.append(filename)
        else:
            assert content is not None
            self.attachments.append((filename, content, mimetype))

    def attach_file(self, path, mimetype=None):
        """
        Attaches a file from the filesystem.

        The mimetype will be set to the DEFAULT_ATTACHMENT_MIME_TYPE if it is
        not specified and cannot be guessed or (PY3 only) if it suggests
        text/* for a binary file.
        """
        filename = os.path.basename(path)
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        basetype, subtype = mimetype.split('/', 1)
        read_mode = 'r' if basetype == 'text' else 'rb'
        content = None

        with open(path, read_mode) as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                # If mimetype suggests the file is text but it's actually
                # binary, read() will raise a UnicodeDecodeError on Python 3.
                pass

        # If the previous read in text mode failed, try binary mode.
        if content is None:
            with open(path, 'rb') as f:
                content = f.read()
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE

        self.attach(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(msg)

    def _create_attachments(self, msg):
        if self.attachments:
            encoding = self.encoding or config['default_charset']
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.mixed_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))
        return msg

    def _create_mime_attachment(self, content, mimetype):
        """
        Converts the content, mimetype pair into a MIME attachment object.

        If the mimetype is message/rfc822, content may be an
        email.Message or EmailMessage object, as well as a str.
        """
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            encoding = self.encoding or config['default_charset']
            attachment = SafeMIMEText(content, subtype, encoding)
        elif basetype == 'message' and subtype == 'rfc822':
            # Bug #18967: per RFC2046 s5.2.1, message/rfc822 attachments
            # must not be base64 encoded.
            if isinstance(content, EmailMessage):
                # convert content into an email.Message first
                content = content.message()
            elif not isinstance(content, Message):
                # For compatibility with existing code, parse the message
                # into an email.Message object if it is not one already.
                content = message_from_string(content)

            attachment = SafeMIMEMessage(content, subtype)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            Encoders.encode_base64(attachment)
        return attachment

    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = DEFAULT_ATTACHMENT_MIME_TYPE
        attachment = self._create_mime_attachment(content, mimetype)
        if filename:
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                filename = ('utf-8', '', filename)
            attachment.add_header('Content-Disposition', 'attachment',
                                  filename=filename)
        return attachment


class EmailMultiAlternatives(EmailMessage):
    """
    A version of EmailMessage that makes it easy to send multipart/alternative
    messages. For example, including text and HTML versions of the text is
    made easier.
    """
    alternative_subtype = 'alternative'

    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, alternatives=None,
                 cc=None, reply_to=None):
        """
        Initialize a single email message (which can be sent to multiple
        recipients).

        All strings used to create the message can be unicode strings (or UTF-8
        bytestrings). The SafeMIMEText class will handle any necessary encoding
        conversions.
        """
        super(EmailMultiAlternatives, self).__init__(
            subject, body, from_email, to, bcc, connection, attachments,
            headers, cc, reply_to,
        )
        self.alternatives = alternatives or []

    def attach_alternative(self, content, mimetype):
        """
        Attach an alternative content representation.
        """
        assert content is not None
        assert mimetype is not None
        self.alternatives.append((content, mimetype))

    def _create_message(self, msg):
        return self._create_attachments(self._create_alternatives(msg))

    def _create_alternatives(self, msg):
        encoding = self.encoding or config['default_charset']
        if self.alternatives:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.alternative_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for alternative in self.alternatives:
                msg.attach(self._create_mime_attachment(*alternative))
        return msg
