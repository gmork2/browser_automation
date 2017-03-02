from datetime import datetime, timedelta, tzinfo

try:
    import pytz
except ImportError:
    pytz = None

from conf import config


class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs. Used only when pytz
    isn't available.
    """
    ZERO = timedelta(0)
    def __repr__(self):return "<UTC>"
    def utcoffset(self, dt):return self.ZERO
    def tzname(self, dt):return "UTC"
    def dst(self, dt):return self.ZERO


def now():
    """
    Returns an aware or naive datetime.datetime, depending on
    config['USE_TZ'].
    """
    utc = pytz.utc if pytz else UTC()
    if config['USE_TZ']:
        # timeit shows that datetime.now(tz=utc) is 24% slower
        return datetime.utcnow().replace(tzinfo=utc)
    else:
        return datetime.now()

