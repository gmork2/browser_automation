from core.webdriver.chromium import constants as command


class WebElement(object):
    """
    Represents an HTML element.
    """
    def __init__(self, chromedriver, id_):
        self._chromedriver = chromedriver
        self._id = id_

    def _execute(self, cmd, params=None):
        if params is None:
            params = {}
        params['id'] = self._id;
        return self._chromedriver.execute_command(cmd, params)

    def find_element(self, strategy, target):
        return self._execute(
            command.FIND_CHILD_ELEMENT, {'using': strategy, 'value': target})

    def find_elements(self, strategy, target):
        return self._execute(
            command.FIND_CHILD_ELEMENTS, {'using': strategy, 'value': target})

    def get_text(self):
        return self._execute(command.GET_ELEMENT_TEXT)

    def get_attribute(self,name):
        return self._execute(command.GET_ELEMENT_ATTRIBUTE, {'name': name})

    def hover_over(self):
        self._execute(command.HOVER_OVER_ELEMENT)

    def click(self):
        self._execute(command.CLICK_ELEMENT)

    def single_tap(self):
        self._execute(command.TOUCH_SINGLE_TAP)

    def double_tap(self):
        self._execute(command.TOUCH_DOUBLE_TAP)

    def long_press(self):
        self._execute(command.TOUCH_LONG_PRESS)

    def clear(self):
        self._execute(command.CLEAR_ELEMENT)

    def send_keys(self, *values):
        typing = []
        for value in values:
          if isinstance(value, int):
            value = str(value)
          for i in range(len(value)):
            typing.append(value[i])
        self._execute(command.SEND_KEYS_TO_ELEMENT, {'value': typing})

    def get_location(self):
        return self._execute(command.GET_ELEMENT_LOCATION)

    def is_displayed(self):
        return self._execute(command.IS_ELEMENT_DISPLAYED)


