# Commands for chromium server
NEW_SESSION = ('POST', '/session')
GET_SESSION_CAPABILITIES = ('GET', '/session/:sessionId')
GET_SESSIONS = ('GET', '/sessions')
QUIT = ('DELETE', '/session/:sessionId')
GET_CURRENT_WINDOW_HANDLE = ('GET', '/session/:sessionId/window_handle')
GET_WINDOW_HANDLES = ('GET', '/session/:sessionId/window_handles')
GET = ('POST', '/session/:sessionId/url')
GET_ALERT = ('GET', '/session/:sessionId/alert')
DISMISS_ALERT = ('POST', '/session/:sessionId/dismiss_alert')
ACCEPT_ALERT = ('POST', '/session/:sessionId/accept_alert')
GET_ALERT_TEXT = ('GET', '/session/:sessionId/alert_text')
SET_ALERT_VALUE = ('POST', '/session/:sessionId/alert_text')
GO_FORWARD = ('POST', '/session/:sessionId/forward')
GO_BACK = ('POST', '/session/:sessionId/back')
REFRESH = ('POST', '/session/:sessionId/refresh')
EXECUTE_SCRIPT = ('POST', '/session/:sessionId/execute')
EXECUTE_ASYNC_SCRIPT = ('POST', '/session/:sessionId/execute_async')

LAUNCH_APP = ('POST', '/session/:sessionId/chromium/launch_app')

GET_CURRENT_URL = ('GET', '/session/:sessionId/url')
GET_TITLE = ('GET', '/session/:sessionId/title')
GET_PAGE_SOURCE = ('GET', '/session/:sessionId/source')
SCREENSHOT = ('GET', '/session/:sessionId/screenshot')
SET_BROWSER_VISIBLE = ('POST', '/session/:sessionId/visible')
IS_BROWSER_VISIBLE = ('GET', '/session/:sessionId/visible')
FIND_ELEMENT = ('POST', '/session/:sessionId/element')
FIND_ELEMENTS = ('POST', '/session/:sessionId/elements')
GET_ACTIVE_ELEMENT = ('POST', '/session/:sessionId/element/active')
FIND_CHILD_ELEMENT = ('POST', '/session/:sessionId/element/:id/element')
FIND_CHILD_ELEMENTS = (
      'POST', '/session/:sessionId/element/:id/elements')
CLICK_ELEMENT = ('POST', '/session/:sessionId/element/:id/click')
CLEAR_ELEMENT = ('POST', '/session/:sessionId/element/:id/clear')
SUBMIT_ELEMENT = ('POST', '/session/:sessionId/element/:id/submit')
GET_ELEMENT_TEXT = ('GET', '/session/:sessionId/element/:id/text')
SEND_KEYS_TO_ELEMENT = ('POST', '/session/:sessionId/element/:id/value')
UPLOAD_FILE = ('POST', '/session/:sessionId/file')
GET_ELEMENT_VALUE = ('GET', '/session/:sessionId/element/:id/value')
GET_ELEMENT_TAG_NAME = ('GET', '/session/:sessionId/element/:id/name')
IS_ELEMENT_SELECTED = (
      'GET', '/session/:sessionId/element/:id/selected')
IS_ELEMENT_ENABLED = ('GET', '/session/:sessionId/element/:id/enabled')
IS_ELEMENT_DISPLAYED = ('GET', '/session/:sessionId/element/:id/displayed')
HOVER_OVER_ELEMENT = ('POST', '/session/:sessionId/element/:id/hover')
GET_ELEMENT_LOCATION = ('GET', '/session/:sessionId/element/:id/location')
GET_ELEMENT_LOCATION_ONCE_SCROLLED_INTO_VIEW = (
    'GET', '/session/:sessionId/element/:id/location_in_view')
GET_ELEMENT_SIZE = ('GET', '/session/:sessionId/element/:id/size')
GET_ELEMENT_ATTRIBUTE = ('GET', '/session/:sessionId/element/:id/attribute/:name')
ELEMENT_EQUALS = ('GET', '/session/:sessionId/element/:id/equals/:other')
GET_COOKIES = ('GET', '/session/:sessionId/cookie')
ADD_COOKIE = ('POST', '/session/:sessionId/cookie')
DELETE_ALL_COOKIES = ('DELETE', '/session/:sessionId/cookie')
DELETE_COOKIE = ('DELETE', '/session/:sessionId/cookie/:name')
SWITCH_TO_FRAME = ('POST', '/session/:sessionId/frame')
SWITCH_TO_PARENT_FRAME = ('POST', '/session/:sessionId/frame/parent')
SWITCH_TO_WINDOW = ('POST', '/session/:sessionId/window')
GET_WINDOW_SIZE = ('GET', '/session/:sessionId/window/:windowHandle/size')
GET_WINDOW_POSITION = ('GET', '/session/:sessionId/window/:windowHandle/position')
SET_WINDOW_SIZE = ('POST', '/session/:sessionId/window/:windowHandle/size')
SET_WINDOW_POSITION = ('POST', '/session/:sessionId/window/:windowHandle/position')
MAXIMIZE_WINDOW = ('POST', '/session/:sessionId/window/:windowHandle/maximize')
CLOSE = ('DELETE', '/session/:sessionId/window')
DRAG_ELEMENT = ('POST', '/session/:sessionId/element/:id/drag')
GET_ELEMENT_VALUE_OF_CSS_PROPERTY = ('GET', '/session/:sessionId/element/:id/css/:propertyName')
IMPLICITLY_WAIT = ('POST', '/session/:sessionId/timeouts/implicit_wait')
SET_SCRIPT_TIMEOUT = ('POST', '/session/:sessionId/timeouts/async_script')
SET_TIMEOUT = ('POST', '/session/:sessionId/timeouts')
EXECUTE_SQL = ('POST', '/session/:sessionId/execute_sql')
GET_LOCATION = ('GET', '/session/:sessionId/location')
SET_LOCATION = ('POST', '/session/:sessionId/location')
GET_NETWORK_CONNECTION = ('GET', '/session/:sessionId/network_connection')

GET_NETWORK_CONDITIONS = ('GET', '/session/:sessionId/chromium/network_conditions')
SET_NETWORK_CONDITIONS = ('POST', '/session/:sessionId/chromium/network_conditions')
DELETE_NETWORK_CONDITIONS = ('DELETE', '/session/:sessionId/chromium/network_conditions')

GET_STATUS = ('GET', '/session/:sessionId/application_cache/status')
IS_BROWSER_ONLINE = ('GET', '/session/:sessionId/browser_connection')
SET_BROWSER_ONLINE = ('POST', '/session/:sessionId/browser_connection')
GET_LOCAL_STORAGE_ITEM = ('GET', '/session/:sessionId/local_storage/key/:key')
REMOVE_LOCAL_STORAGE_ITEM = ('DELETE', '/session/:sessionId/local_storage/key/:key')
GET_LOCAL_STORAGE_KEYS = ('GET', '/session/:sessionId/local_storage')
SET_LOCAL_STORAGE_ITEM = ('POST', '/session/:sessionId/local_storage')
CLEAR_LOCAL_STORAGE = ('DELETE', '/session/:sessionId/local_storage')
GET_LOCAL_STORAGE_SIZE = ('GET', '/session/:sessionId/local_storage/size')
GET_SESSION_STORAGE_ITEM = ('GET', '/session/:sessionId/session_storage/key/:key')
REMOVE_SESSION_STORAGE_ITEM = ('DELETE', '/session/:sessionId/session_storage/key/:key')
GET_SESSION_STORAGE_KEY = ('GET', '/session/:sessionId/session_storage')
SET_SESSION_STORAGE_ITEM = ('POST', '/session/:sessionId/session_storage')
CLEAR_SESSION_STORAGE = ('DELETE', '/session/:sessionId/session_storage')
GET_SESSION_STORAGE_SIZE = ('GET', '/session/:sessionId/session_storage/size')
GET_SCREEN_ORIENTATION = ('GET', '/session/:sessionId/orientation')
SET_SCREEN_ORIENTATION = ('POST', '/session/:sessionId/orientation')
DELETE_SCREEN_ORIENTATION = ('DELETE', '/session/:sessionId/orientation')
MOUSE_CLICK = ('POST', '/session/:sessionId/click')
MOUSE_DOUBLE_CLICK = ('POST', '/session/:sessionId/doubleclick')
MOUSE_BUTTON_DOWN = ('POST', '/session/:sessionId/buttondown')
MOUSE_BUTTON_UP = ('POST', '/session/:sessionId/buttonup')
MOUSE_MOVE_TO = ('POST', '/session/:sessionId/moveto')
SEND_KEYS_TO_ACTIVE_ELEMENT = ('POST', '/session/:sessionId/keys')
TOUCH_SINGLE_TAP = ('POST', '/session/:sessionId/touch/click')
TOUCH_DOWN = ('POST', '/session/:sessionId/touch/down')
TOUCH_UP = ('POST', '/session/:sessionId/touch/up')
TOUCH_MOVE = ('POST', '/session/:sessionId/touch/move')
TOUCH_SCROLL = ('POST', '/session/:sessionId/touch/scroll')
TOUCH_DOUBLE_TAP = ('POST', '/session/:sessionId/touch/doubleclick')
TOUCH_LONG_PRESS = ('POST', '/session/:sessionId/touch/longclick')
TOUCH_FLICK = ('POST', '/session/:sessionId/touch/flick')
GET_LOG = ('POST', '/session/:sessionId/log')
GET_AVAILABLE_LOG_TYPES = ('GET', '/session/:sessionId/log/types')
IS_AUTO_REPORTING = ('GET', '/session/:sessionId/autoreport')
SET_AUTO_REPORTING = ('POST', '/session/:sessionId/autoreport')
GET_SESSION_LOGS = ('POST', '/logs')
STATUS = ('GET', '/status')
SHUTDOWN = ('GET', '/shutdown')
SET_NETWORK_CONNECTION = ('POST', '/session/:sessionId/network_connection')

# Custom Chrome commands.
IS_LOADING = ('GET', '/session/:sessionId/is_loading')
TOUCH_PINCH = ('POST', '/session/:sessionId/touch/pinch')