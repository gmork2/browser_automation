import logging
import os
import unittest

from conf import config
from core.services.connection import LiveServerThread
from utils.decorators import classproperty


logger = logging.getLogger(__name__)

class LiveServerTestCase(unittest.TestCase):
    """
    Does basically the same as TestCase but also launches a live
    http server in a separate thread so that the tasks may use,
    for example, selenium standalone server instead of run tasks on
    local machine.
    """
    @classproperty
    def live_server_url(cls):# @NoSelf
        return 'http://%s:%s' % (
            cls.server_thread.host, cls.server_thread.port)

    @classmethod
    def setUpClass(cls):
        super(LiveServerTestCase, cls).setUpClass()
        specified_address = os.environ.get(
            'BROWSER_AUTOMATION_SERVER_ADDRESS',
            '{0}:{1}'.format(config['service_host'], config['service_port'])
        )

        # The specified ports may be of the form '8000-8010,8080,9200-9300'
        # i.e. a comma-separated list of ports or ranges of ports, so we break
        # it down into a detailed list of all possible ports.
        possible_ports = []
        try:
            host, port_ranges = specified_address.split(':')
            for port_range in port_ranges.split(','):
                # A port range can be of either form: '8000' or '8000-8010'.
                extremes = list(map(int, port_range.split('-')))
                assert len(extremes) in [1, 2]
                if len(extremes) == 1:
                    # Port range of the form '8000'
                    possible_ports.append(extremes[0])
                else:
                    # Port range of the form '8000-8010'
                    for port in range(extremes[0], extremes[1] + 1):
                        possible_ports.append(port)
        except Exception:
            msg = 'Invalid address ("%s") for live server.' % specified_address
            print(msg)

        # Launch the live server's thread
        cls.server_thread = cls._create_server_thread(host, possible_ports)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the live server to be ready
        cls.server_thread.is_ready.wait()
        if cls.server_thread.error:
            # Clean up behind ourselves, since tearDownClass won't get called in
            # case of errors.
            cls._tearDownClassInternal()
            raise cls.server_thread.error

    @classmethod
    def _create_server_thread(cls, host, possible_ports):
        return LiveServerThread(
            host,
            possible_ports,
        )

    @classmethod
    def _tearDownClassInternal(cls):
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(cls, 'server_thread'):
            # Terminate the live server's thread
            cls.server_thread.terminate()
            cls.server_thread.join()

    @classmethod
    def tearDownClass(cls):
        cls._tearDownClassInternal()
        #type, value, traceback = sys.exc_info()
        super(LiveServerTestCase, cls).tearDownClass()

