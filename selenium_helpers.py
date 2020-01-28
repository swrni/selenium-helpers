#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has helper functions for using Selenium."""

import os
import time
from contextlib import contextmanager, suppress

import selenium
from selenium.webdriver.remote.command import Command
from selenium.webdriver.chrome.options import Options

import selenium.common.exceptions as selenium_exceptions
WebDriverException = selenium_exceptions.WebDriverException
NoAlertPresentException = selenium_exceptions.NoAlertPresentException

import session
import service
from repeat_on_failure import ReTry

class InvalidXPath(Exception):
    """Custom exception for invalid xpath."""

class Settings:
    def __init__(self):
        self.change_page_delay = 2
        self.click_delay = 1
        self.send_keys_delay = 1

        self.try_times = 10
        self.sleep_time = 1

    def get_default_re_try(self):
        return ReTry(WebDriverException,
            tries=self.try_times,
            sleep_time=self.sleep_time
        )

    def get_alerts_re_try(self):
        return ReTry(
            NoAlertPresentException,
            tries=self.try_times,
            sleep_time=self.sleep_time
        )

def _get_default_options():
    """Return the default options for a new driver."""

    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("disable-infobars")
    return options

class Driver(selenium.webdriver.remote.webdriver.WebDriver):
    """Remote driver class that uses an existing session when possible."""

    @staticmethod
    def create():
        """Return instance of 'Driver' and start the 'chromedriver' service if needed."""

        # Use the default port if custom port is not found in environment.
        service._start_chromedriver()

        options = _get_default_options()
        port = os.environ.get(service.PORT_ENV_KEY, service.DEFAULT_PORT)
        session_id = session._read_session_id()

        with suppress(selenium.common.exceptions.WebDriverException):
            driver = Driver(options, Settings(), port=port, session_id=session_id)
            session._save_session_id(driver.session_id)
            return driver

        session._clear_session_id()

        driver = Driver(options, Settings(), port=port)
        session._save_session_id(driver.session_id)
        return driver

    def __init__(self, options, settings, port=None, session_id=None):
        """Initialize 'Driver'."""

        if not isinstance(options, Options):
            raise TypeError(f"Invalid type: {type(options)}")

        if not isinstance(settings, Settings):
            raise TypeError(f"Invalid type: {type(settings)}")

        self.settings = settings

        url = f"http://127.0.0.1:{port}"
        self._saved_session_id = session_id

        super().__init__(command_executor=url, desired_capabilities={}, options=options)

        # Verify that the browser opened.
        self.current_url

    def execute(self, driver_command, params=None):
        """Override 'super().execute()' so existing session is used."""

        if driver_command == Command.NEW_SESSION and self._saved_session_id:
            return {"success": 0, "value": None, "sessionId": self._saved_session_id}
        return super().execute(driver_command, params=params)

    def find_by_xpath(self, xpath, many=False):
        """
        Wrapper for calling 'self.find_element_by_xpath(xpath)'. If 'many' is 'True', return a list
        of elements, instead of the first found.
        """

        def implementation():
            """Wrapped function implementation."""

            if many:
                return self.find_elements_by_xpath(xpath)
            return self.find_element_by_xpath(xpath)

        return self.settings.get_default_re_try()(implementation)()

    def click_by_xpath(self, xpath, send_js_event=False, root_element=None):
        """Find and click the first element matching 'xpath' and 'root_element'."""

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath, many=False)
            if send_js_event:
                self.execute_script("arguments[0].click();", element)
            else:
                element.click()
            time.sleep(self.settings.click_delay)
            return element

        return self.settings.get_default_re_try()(implementation)()

    def read_text_by_xpath(self, xpath, allow_empty=True):
        """
        Find the first element matching 'xpath' and 'root_element' and return its text. If
        'allow_empty' is 'False' and the text is empty, raise 'WebDriverException'.
        """

        def implementation():
            """Wrapped function implementation."""

            text = self.find_by_xpath(xpath, many=False).text
            if not text and not allow_empty:
                raise WebDriverException(f"Text empty: '{xpath}'")
            return text

        return self.settings.get_default_re_try()(implementation)()

    def read_attribute_by_xpath(self, xpath, attribute):
        """
        Find the first element matching 'xpath' and 'root_element', call its method
        'get_attribute(<attribute>)' and return it. 'xpath' and 'root_element' are passed to
        'find_by_xpath()'.
        """

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath, many=False)
            return element.get_attribute(attribute)

        return self.settings.get_default_re_try()(implementation)()

    def send_keys_by_xpath(self, xpath, keys):
        """
        Find the first element matching 'xpath' and 'root_element' and try to change its value to
        'keys'.
        """

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath)

            element.clear()
            time.sleep(self.settings.send_keys_delay)

            element.send_keys(keys)
            time.sleep(self.settings.send_keys_delay)

            element_value = element.get_attribute("value")
            if element_value != keys:
                raise WebDriverException(f"Element's value does not match with sent keys:\n"
                                         f"'{element_value}' and '{keys}'")
            return element

        if not isinstance(keys, str):
            keys = f"{keys}"
        return self.settings.get_default_re_try()(implementation)()

    def set_value(self, xpath, value):
        """Set value of the element matching 'xpath' to 'value'."""

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath)
            self.execute_script(f"arguments[0].value='{value}';", element)
            if self.read_attribute_by_xpath(xpath, "value") != value:
                raise WebDriverException

        self.settings.get_default_re_try()(implementation)()

    @contextmanager
    def open_url(self, url, go_back=True, refresh=False):
        """
        Open the 'url'. If 'go_back' is 'True', go back to the original url afterwards. If 'refresh' is
        'True', open the 'url' even if it is already open.

        Can be used like this:
        > with open_url("google.com"):
        >     print("Now at 'google.com'")
        > print("Now at starting url.")
        """

        def go_to(new_url):
            """
            Go to 'url' if it is a different page than the current one, or if 'refresh' is 'True'.
            """

            is_new_url = new_url != self.current_url
            if refresh or is_new_url:
                self.get(new_url)
                time.sleep(self.settings.change_page_delay)

        original_url = self.current_url
        go_to(url)
        yield
        if go_back:
            go_to(original_url)

    def accept_alert(self):
        """Close alert by clicking 'OK'."""

        def implementation():
            """Wrapped function implementation."""

            self.switch_to.alert.accept()
        self.settings.get_alerts_re_try()(implementation)()

    def cancel_alert(self):
        """Close alert by clicking 'Cancel'."""

        def implementation():
            """Wrapped function implementation."""

            self.switch_to.alert.dismiss()
        self.settings.get_alerts_re_try()(implementation)()

    def shutdown(self):
        """Close the window and shutdown the 'chromedriver'."""

        self.quit()
        session._clear_session_id()
        service._shutdown_chromedriver()
