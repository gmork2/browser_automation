import platform
import sys

from core.webdriver.chromium import constants as command
from core.webdriver.chromium.controller import Controller
from core.webdriver.chromium.webelement import WebElement
from core.webdriver.exceptions import (
    UnknownError, exception_for_legacy_response, exception_for_standard_response)

ELEMENT_KEY_W3C = "element-6066-11e4-a52e-4f735466cecf"
ELEMENT_KEY = "ELEMENT"


class ChromiumDriver(object):
    """
    Starts and controls a single Chrome instance on this machine.
    """

    def __init__(self, server_url, chrome_binary=None, android_package=None,
                 android_activity=None, android_process=None,
                 android_use_running_app=None, chrome_switches=None,
                 chrome_extensions=None, chrome_log_path=None,
                 debugger_address=None, logging_prefs=None,
                 mobile_emulation=None, experimental_options=None,
                 download_dir=None, network_connection=None,
                 send_w3c_capability=None, send_w3c_request=None,
                 page_load_strategy=None, unexpected_alert_behaviour=None):
        self._executor = Controller(server_url)

        options = {}

        if experimental_options:
            assert isinstance(experimental_options, dict)
            options = experimental_options.copy()

        if android_package:
            options['androidPackage'] = android_package
            if android_activity:
                options['androidActivity'] = android_activity
            if android_process:
                options['androidProcess'] = android_process
            if android_use_running_app:
                options['androidUseRunningApp'] = android_use_running_app
        elif chrome_binary:
            options['binary'] = chrome_binary

        # TODO(samuong): speculative fix for crbug.com/611886
        if (sys.platform.startswith('linux') and
                    platform.architecture()[0] == '32bit'):
            if chrome_switches is None:
                chrome_switches = []
            chrome_switches.append('no-sandbox')

        if chrome_switches:
            assert type(chrome_switches) is list
            options['args'] = chrome_switches

        if mobile_emulation:
            assert type(mobile_emulation) is dict
            options['mobileEmulation'] = mobile_emulation

        if chrome_extensions:
            assert type(chrome_extensions) is list
            options['extensions'] = chrome_extensions

        if chrome_log_path:
            assert type(chrome_log_path) is str
            options['logPath'] = chrome_log_path

        if debugger_address:
            assert type(debugger_address) is str
            options['debuggerAddress'] = debugger_address

        if logging_prefs:
            assert type(logging_prefs) is dict
            log_types = ['client', 'driver', 'browser', 'server', 'performance']
            log_levels = ['ALL', 'DEBUG', 'INFO', 'WARNING', 'SEVERE', 'OFF']
            for log_type, log_level in logging_prefs.iteritems():
                assert log_type in log_types
                assert log_level in log_levels
        else:
            logging_prefs = {}

        download_prefs = {}
        if download_dir:
            if 'prefs' not in options:
                options['prefs'] = {}
            if 'download' not in options['prefs']:
                options['prefs']['download'] = {}
            options['prefs']['download']['default_directory'] = download_dir

        if send_w3c_capability:
            options['w3c'] = send_w3c_capability

        params = {
            'desiredCapabilities': {
                'chromeOptions': options,
                'loggingPrefs': logging_prefs
            }
        }

        if page_load_strategy:
            assert type(page_load_strategy) is str
            params['desiredCapabilities']['pageLoadStrategy'] = page_load_strategy

        if unexpected_alert_behaviour:
            assert type(unexpected_alert_behaviour) is str
            params['desiredCapabilities']['unexpectedAlertBehaviour'] = (
                unexpected_alert_behaviour)

        if network_connection:
            params['desiredCapabilities']['networkConnectionEnabled'] = (
                network_connection)

        if send_w3c_request:
            params = {'capabilities': params}

        response = self._execute_command(command.NEW_SESSION, params)
        if isinstance(response['status'], str):
            self.w3c_compliant = True
        elif isinstance(response['status'], int):
            self.w3c_compliant = False
        else:
            raise UnknownError("unexpected response")

        self._session_id = response['sessionId']
        self.capabilities = self._unwrap_value(response['value'])


    def _wrap_value(self, value):
        """
        Wrap value from client side for chromedriver side.
        """
        if isinstance(value, dict):
            converted = {}
            for key, val in value.items():
                converted[key] = self._wrap_value(val)
            return converted
        elif isinstance(value, WebElement):
            if (self.w3c_compliant):
                return {ELEMENT_KEY_W3C: value._id}
            else:
                return {ELEMENT_KEY: value._id}
        elif isinstance(value, list):
            return list(self._wrap_value(item) for item in value)
        else:
            return value

    def _unwrap_value(self, value):
        if isinstance(value, dict):
            if (self.w3c_compliant and len(value) == 1
                and ELEMENT_KEY_W3C in value
                and isinstance(
                    value[ELEMENT_KEY_W3C], str)):
                return WebElement(self, value[ELEMENT_KEY_W3C])
            elif (len(value) == 1 and ELEMENT_KEY in value
                  and isinstance(value[ELEMENT_KEY], str)):
                return WebElement(self, value[ELEMENT_KEY])
            else:
                unwraped = {}
                for key, val in value.items():
                    unwraped[key] = self._unwrap_value(val)
                return unwraped
        elif isinstance(value, list):
            return list(self._unwrap_value(item) for item in value)
        else:
            return value

    def _execute_command(self, command, params={}):
        params = self._wrap_value(params)
        response = self._executor.execute(command, params)
        if ('status' in response and isinstance(response['status'], int) and
                    response['status'] != 0):
            raise exception_for_legacy_response(response)
        elif 'error' in response:
            raise exception_for_standard_response(response)
        return response

    def execute_command(self, command, params={}):
        params['sessionId'] = self._session_id
        response = self._execute_command(command, params)
        return self._unwrap_value(response['value'])

    def get_window_handles(self):
        return self.execute_command(command.GET_WINDOW_HANDLES)

    def switch_to_window(self, handle_or_name):
        self.execute_command(command.SWITCH_TO_WINDOW, {'name': handle_or_name})

    def get_current_window_handle(self):
        return self.execute_command(command.GET_CURRENT_WINDOW_HANDLE)

    def close_window(self):
        self.execute_command(command.CLOSE)

    def load(self, url):
        self.execute_command(command.GET, {'url': url})

    def launch_app(self, app_id):
        self.execute_command(command.LAUNCH_APP, {'id': app_id})

    def execute_script(self, script, *args):
        converted_args = list(args)
        return self.execute_command(
            command.EXECUTE_SCRIPT, {'script': script, 'args': converted_args})

    def execute_async_script(self, script, *args):
        converted_args = list(args)
        return self.execute_command(
            command.EXECUTE_ASYNC_SCRIPT,
            {'script': script, 'args': converted_args})

    def switch_to_frame(self, id_or_name):
        self.execute_command(command.SWITCH_TO_FRAME, {'id': id_or_name})

    def switch_to_frame_by_index(self, index):
        self.switch_to_frame(index)

    def switch_to_main_frame(self):
        self.switch_to_frame(None)

    def switch_to_parent_frame(self):
        self.execute_command(command.SWITCH_TO_PARENT_FRAME)

    def get_sessions(self):
        return self.execute_command(command.GET_SESSIONS)

    def get_title(self):
        return self.execute_command(command.GET_TITLE)

    def get_page_source(self):
        return self.execute_command(command.GET_PAGE_SOURCE)

    def find_element(self, strategy, target):
        return self.execute_command(
            command.FIND_ELEMENT, {'using': strategy, 'value': target})

    def find_elements(self, strategy, target):
        return self.execute_command(
            command.FIND_ELEMENTS, {'using': strategy, 'value': target})

    def set_timeout(self, type, timeout):
        return self.execute_command(
            command.SET_TIMEOUT, {'type' : type, 'ms': timeout})

    def get_current_url(self):
        return self.execute_command(command.GET_CURRENT_URL)

    def go_back(self):
        return self.execute_command(command.GO_BACK)

    def go_forward(self):
        return self.execute_command(command.GO_FORWARD)

    def refresh(self):
        return self.execute_command(command.REFRESH)

    def mouse_move_to(self, element=None, x_offset=None, y_offset=None):
        params = {}
        if element is not None:
            params['element'] = element._id
        if x_offset is not None:
            params['xoffset'] = x_offset
        if y_offset is not None:
            params['yoffset'] = y_offset
        self.execute_command(command.MOUSE_MOVE_TO, params)

    def mouse_click(self, button=0):
        self.execute_command(command.MOUSE_CLICK, {'button': button})

    def mouse_button_down(self, button=0):
        self.execute_command(command.MOUSE_BUTTON_DOWN, {'button': button})

    def mouse_button_up(self, button=0):
        self.execute_command(command.MOUSE_BUTTON_UP, {'button': button})

    def mouse_double_click(self, button=0):
        self.execute_command(command.MOUSE_DOUBLE_CLICK, {'button': button})

    def touch_down(self, x, y):
        self.execute_command(command.TOUCH_DOWN, {'x': x, 'y': y})

    def touch_up(self, x, y):
        self.execute_command(command.TOUCH_UP, {'x': x, 'y': y})

    def touch_move(self, x, y):
        self.execute_command(command.TOUCH_MOVE, {'x': x, 'y': y})

    def touch_scroll(self, element, xoffset, yoffset):
        params = {'element': element._id, 'xoffset': xoffset, 'yoffset': yoffset}
        self.execute_command(command.TOUCH_SCROLL, params)

    def touch_flick(self, element, xoffset, yoffset, speed):
        params = {
            'element': element._id,
            'xoffset': xoffset,
            'yoffset': yoffset,
            'speed': speed
        }
        self.execute_command(command.TOUCH_FLICK, params)

    def touch_pinch(self, x, y, scale):
        params = {'x': x, 'y': y, 'scale': scale}
        self.execute_command(command.TOUCH_PINCH, params)

    def get_cookies(self):
        return self.execute_command(command.GET_COOKIES)

    def add_cookie(self, cookie):
        self.execute_command(command.ADD_COOKIE, {'cookie': cookie})

    def delete_cookie(self, name):
        self.execute_command(command.DELETE_COOKIE, {'name': name})

    def delete_all_cookies(self):
        self.execute_command(command.DELETE_ALL_COOKIES)

    def is_alert_open(self):
        return self.execute_command(command.GET_ALERT)

    def get_alert_message(self):
        return self.execute_command(command.GET_ALERT_TEXT)

    def handle_alert(self, accept, prompt_text=''):
        if prompt_text:
            self.execute_command(command.SET_ALERT_VALUE, {'text': prompt_text})
        if accept:
            cmd = command.ACCEPT_ALERT
        else:
            cmd = command.DISMISS_ALERT
        self.execute_command(cmd)

    def is_loading(self):
        return self.execute_command(command.IS_LOADING)

    def get_window_position(self):
        position = self.execute_command(command.GET_WINDOW_POSITION,
                                       {'windowHandle': 'current'})
        return [position['x'], position['y']]

    def set_window_position(self, x, y):
        self.execute_command(command.SET_WINDOW_POSITION,
                            {'windowHandle': 'current', 'x': x, 'y': y})

    def get_window_size(self):
        size = self.execute_command(command.GET_WINDOW_SIZE,
                                   {'windowHandle': 'current'})
        return [size['width'], size['height']]

    def set_window_size(self, width, height):
        self.execute_command(
            command.SET_WINDOW_SIZE,
            {'windowHandle': 'current', 'width': width, 'height': height})

    def maximize_window(self):
        self.execute_command(command.MAXIMIZE_WINDOW, {'windowHandle': 'current'})

    def quit(self):
        """
        Quits the browser and ends the session.
        """
        self.execute_command(command.QUIT)

    def get_log(self, type):
        return self.execute_command(command.GET_LOG, {'type': type})

    def GetAvailableLogTypes(self):
        return self.execute_command(command.GET_AVAILABLE_LOG_TYPES)

    def is_auto_reporting(self):
        return self.execute_command(command.IS_AUTO_REPORTING)

    def set_auto_reporting(self, enabled):
        self.execute_command(command.SET_AUTO_REPORTING, {'enabled': enabled})

    def set_network_conditions(self, latency, download_throughput,
                             upload_throughput, offline=False):
        # Until http://crbug.com/456324 is resolved, we'll always set 'offline' to
        # False, as going "offline" will sever Chromedriver's connection to Chrome.
        params = {
            'network_conditions': {
                'offline': offline,
                'latency': latency,
                'download_throughput': download_throughput,
                'upload_throughput': upload_throughput
            }
        }
        self.execute_command(command.SET_NETWORK_CONDITIONS, params)

    def set_network_conditions_name(self, network_name):
        self.execute_command(
            command.SET_NETWORK_CONDITIONS, {'network_name': network_name})

    def get_network_conditions(self):
        conditions = self.execute_command(command.GET_NETWORK_CONDITIONS)
        return {
            'latency': conditions['latency'],
            'download_throughput': conditions['download_throughput'],
            'upload_throughput': conditions['upload_throughput'],
            'offline': conditions['offline']
        }

    def get_network_connection(self):
        return self.execute_command(command.GET_NETWORK_CONNECTION)

    def delete_network_conditions(self):
        self.execute_command(command.DELETE_NETWORK_CONDITIONS)

    def set_network_connection(self, connection_type):
        params = {'parameters': {'type': connection_type}}
        return self.execute_command(command.SET_NETWORK_CONNECTION, params)

    def get_screen_orientation(self):
        screen_orientation = self.execute_command(command.GET_SCREEN_ORIENTATION)
        return {
            'orientation': screen_orientation['orientation']
        }

    def set_screen_orientation(self, orientation_type):
        params = {'parameters': {'orientation': orientation_type}}
        self.execute_command(command.SET_SCREEN_ORIENTATION, params)

    def delete_screen_orientation_lock(self):
        self.execute_command(command.DELETE_SCREEN_ORIENTATION)

    def send_keys(self, *values):
        typing = []
        for value in values:
            if isinstance(value, int):
                value = str(value)
            for i in range(len(value)):
                typing.append(value[i])
        self.execute_command(command.SEND_KEYS_TO_ACTIVE_ELEMENT, {'value': typing})

