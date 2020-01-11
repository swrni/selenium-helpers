#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has helper functions for using Selenium."""

import time
from contextlib import contextmanager

import selenium.common.exceptions as selenium_exceptions
WebDriverException = selenium_exceptions.WebDriverException
NoAlertPresentException = selenium_exceptions.NoAlertPresentException

import _web_driver
from repeat_on_failure import ReTry

class InvalidXPath(Exception):
    """Custom exception for invalid xpath."""

class Options:
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

class Driver:
    def __init__(self, driver=None, options=None):
        if not options:
            options = Options()
        if not isinstance(options, Options):
            raise TypeError(f"Invalid type: {type(options)}")

        self._driver = driver
        self.options = options

    def _validate_root_element(self, xpath, root_element):
        """
        Verify that 'xpath' and 'root_element' are valid and return validated 'root_element'. Otherwise
        raise 'InvalidXPath' exception.
        """

        if not root_element:
            root_element = self.driver

        # pylint: disable=protected-access
        if xpath.startswith("./") and isinstance(root_element, _web_driver._WebDriver):
            raise InvalidXPath
        if xpath.startswith("//") and not isinstance(root_element, _web_driver._WebDriver):
            raise InvalidXPath
        return root_element

    def find_by_xpath(self, xpath, root_element=None, many=False):
        """
        Wrapper for calling 'root_element.find_element_by_xpath(xpath)'. If 'root_element' is 'None',
        'self.driver' is used instead. If 'many' is 'True', return a list of elements, instead of the
        first found.
        """

        def implementation():
            """Wrapped function implementation."""

            if many:
                return root_element.find_elements_by_xpath(xpath)
            return root_element.find_element_by_xpath(xpath)

        root_element = self._validate_root_element(xpath, root_element)
        return self.options.get_default_re_try()(implementation)()

    def click_by_xpath(self, xpath, send_js_event=False, root_element=None):
        """Find and click the first element matching 'xpath' and 'root_element'."""

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath, root_element=root_element, many=False)
            if send_js_event:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            time.sleep(self.options.click_delay)
            return element

        return self.options.get_default_re_try()(implementation)()

    def read_text_by_xpath(self, xpath, root_element=None, allow_empty=True):
        """
        Find the first element matching 'xpath' and 'root_element' and return its text. If
        'allow_empty' is 'False' and the text is empty, raise 'WebDriverException'.
        """

        def implementation():
            """Wrapped function implementation."""

            text = self.find_by_xpath(xpath, root_element=root_element, many=False).text
            if not text and not allow_empty:
                raise WebDriverException(f"Text empty: '{xpath}'")
            return text

        return self.options.get_default_re_try()(implementation)()

    def read_attribute_by_xpath(self, xpath, attribute, root_element=None):
        """
        Find the first element matching 'xpath' and 'root_element', call its method
        'get_attribute(<attribute>)' and return it. 'xpath' and 'root_element' are passed to
        'find_by_xpath()'.
        """

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath, root_element=root_element, many=False)
            return element.get_attribute(attribute)

        return self.options.get_default_re_try()(implementation)()

    def send_keys_by_xpath(self, xpath, keys, root_element=None):
        """
        Find the first element matching 'xpath' and 'root_element' and try to change its value to
        'keys'.
        """

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath, root_element=root_element)

            element.clear()
            time.sleep(self.options.send_keys_delay)

            element.send_keys(keys)
            time.sleep(self.options.send_keys_delay)

            element_value = element.get_attribute("value")
            if element_value != keys:
                raise WebDriverException(f"Element's value does not match with sent keys:\n"
                                         f"'{element_value}' and '{keys}'")
            return element

        if not isinstance(keys, str):
            keys = f"{keys}"
        return self.options.get_default_re_try()(implementation)()

    def set_value(self, xpath, value):
        """Set value of the element matching 'xpath' to 'value'."""

        def implementation():
            """Wrapped function implementation."""

            element = self.find_by_xpath(xpath)
            self.driver.execute_script(f"arguments[0].value='{value}';", element)
            if self.read_attribute_by_xpath(xpath, "value") != value:
                raise WebDriverException

        self.options.get_default_re_try()(implementation)()

    @property
    def driver(self):
        """Return driver instance."""

        if self._driver:
            return self._driver
        return _web_driver.get_driver()

    @property
    def current_url(self):
        """Return current url."""

        return self.driver.current_url

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
                self.driver.get(new_url)
                time.sleep(self.options.change_page_delay)

        original_url = self.current_url
        go_to(url)
        yield
        if go_back:
            go_to(original_url)

    def accept_alert(self):
        """Close alert by clicking 'OK'."""

        def implementation():
            """Wrapped function implementation."""

            self.driver.switch_to.alert.accept()
        self.options.get_alerts_re_try()(implementation)()

    def cancel_alert(self):
        """Close alert by clicking 'Cancel'."""

        def implementation():
            """Wrapped function implementation."""

            self.driver.switch_to.alert.dismiss()
        self.options.get_alerts_re_try()(implementation)()

    def close(self):
        """Close the window."""

        self.driver.close()

    def shutdown(self):
        """Close the window and shutdown the 'chromedriver'."""

        self.driver.quit()
        _web_driver.shutdown()
