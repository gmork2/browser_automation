import errno
import logging
import os
import socket
import threading
from urllib import request

from core.webdriver.chromium import constants as command

logger = logging.getLogger(__name__)


class LiveServerThread(threading.Thread):
    """
    Thread for running a live http server while the tasks are running.
    """

    def __init__(self, host, possible_ports, env=None):
        self.host = host
        self.port = None
        self.possible_ports = possible_ports
        self.env = env or os.environ
        self.is_ready = threading.Event()
        self.error = None
        super(LiveServerThread, self).__init__()

    def run(self):
        """
        Sets up the live server and then loops over handling
        http requests.
        """
        try:
            # Go through the list of possible ports, hoping that we can find
            # one that is free to use for the service server.
            for index, port in enumerate(self.possible_ports):
                try:
                    self.process = self._create_server(port)
                except socket.error as e:
                    if (index + 1 < len(self.possible_ports) and
                            e.errno == errno.EADDRINUSE):
                        # This port is already in use, so we go on and try with
                        # the next one in the list.
                        continue
                    else:
                        # Either none of the given ports are free or the error
                        # is something else than "Address already in use". So
                        # we let that error bubble up to the main thread.
                        raise
                else:
                    # A free port was found.
                    self.port = port
                    break

            self.is_ready.set()

        except Exception as e:
            self.error = e
            self.is_ready.set()

    def get_url(self):
        return 'http://%s:%s' % (self.host, self.port)

    def is_running(self):
        """
        Returns whether the server is up and running.
        """
        socket_ = None
        try:
            socket_ = socket.create_connection((self.host, self.port), 1)
            result = True
        except socket.error:
            result = False
        finally:
            if socket_:
                socket_.close()
        return result

    def get_status(self):
        try:
            response = request.urlopen(self.get_url() + '/status')
        except request.URLError:
            response = None
        return response

    def _create_server(self, port):
        raise NotImplemented

    def terminate(self):
        try:
            if hasattr(self, 'process') and self.process:
                try:
                    cmd = self.get_url() + command.SHUTDOWN[1]
                    request.urlopen(cmd, timeout=10).close()
                except:
                    logger.warning("Error trying to shutdown server")

                for stream in [self.process.stdin,
                               self.process.stdout,
                               self.process.stderr]:
                    try:
                        stream.close()
                    except AttributeError:
                        pass

                self.process.terminate()
                self.process.kill()
                self.process.wait()
                self.process = None
        except OSError:
            logger.error('Kill server may not be available under windows environment')

    def __del__(self):
        # subprocess.Popen doesn't send signal on __del__;
        # we have to try to terminate the launched process.
        self.terminate()





