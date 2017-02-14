import http.client as http_client
import json

import logging


logger = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, server_url):
        self._server_url = server_url
        port = int(server_url.split(':')[2].split('/')[0])
        self._conn = http_client.HTTPConnection('127.0.0.1', port, timeout=30)


    def execute(self, command, params):
        """
        Send a command to the remote server.

        Any path subtitutions required for the URL mapped to the command should be
        included in the command parameters.
        """

        url_parts = command[1].split('/')
        substituted_parts = []
        for part in url_parts:
            if part.startswith(':'):
                key = part[1:]
                substituted_parts += [params[key]]
                del params[key]
            else:
                substituted_parts += [part]

        body = None
        if command[0] == 'POST':
            body = json.dumps(params)

        self._conn.request(command[0], '/'.join(substituted_parts), body)
        response = self._conn.getresponse()

        if response.status == 303:
            self._conn.request('GET', response.getheader('location'))
            response = self._conn.getresponse()

        r = response.read().decode("utf-8")
        result = json.loads(r)

        if response.status != 200 and 'error' not in result:
            raise RuntimeError('Server returned error: ' + response.reason)
        return result

