#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has helper functions for using Selenium."""

import time
from contextlib import contextmanager

from selenium.common.exceptions import WebDriverException, NoAlertPresentException

import _web_driver
from repeat_on_failure import ReTry

# pylint: disable=invalid-name
RepeatOnWebDriverException = ReTry(WebDriverException)
RepeatOnNoAlertPresentException = ReTry(NoAlertPresentException)

_DRIVER = None

def _init_driver():
    """Initialize '_DRIVER'."""

    global _DRIVER
    _DRIVER = _web_driver.get_driver()

def get_driver():
    """Cache and return the driver."""

    if not _DRIVER:
        _init_driver()
    return _DRIVER

def shutdown():
    """Shutdown session."""

    global _DRIVER
    if _DRIVER:
        _DRIVER.quit()
        _DRIVER = None
    _web_driver.shutdown()

class InvalidXPath(Exception):
    """Custom exception for invalid xpath."""

def _validate_root_element(xpath, root_element):
    """
    Verify that 'xpath' and 'root_element' are valid and return validated 'root_element'. Otherwise
    raise 'InvalidXPath' exception.
    """

    if not root_element:
        root_element = get_driver()

    # pylint: disable=protected-access
    if xpath.startswith("./") and isinstance(root_element, _web_driver._WebDriver):
        raise InvalidXPath("'xpath' starting with: './', requires a 'root_element'")
    if xpath.startswith("//") and not isinstance(root_element, _web_driver._WebDriver):
        raise InvalidXPath("'xpath' starting with: '//', requires that no 'root_element' is "
                           "passed")
    return root_element

def _find_by_xpath(xpath, root_element=None, many=False):
    """
    Wrapper for calling 'root_element.find_element_by_xpath(xpath)'. If 'root_element' is 'None',
    cached driver is used instead. If 'many' is 'True', return a list of elements, instead of the
    first found.
    """

    root_element = _validate_root_element(xpath, root_element)
    if many:
        return root_element.find_elements_by_xpath(xpath)
    return root_element.find_element_by_xpath(xpath)

@RepeatOnWebDriverException
def find_by_xpath(xpath, root_element=None, many=False):
    """Decorated '_find_by_xpath()' call."""

    return _find_by_xpath(xpath, root_element=root_element, many=many)

def _click_by_xpath(xpath, root_element=None):
    """Find and click the first element matching 'xpath' and 'root_element'."""

    root_element = _validate_root_element(xpath, root_element)
    element = find_by_xpath(xpath, root_element=root_element, many=False)
    element.click() # TODO:: Change this to javascript '.click()'.
    return element

@RepeatOnWebDriverException
def click_by_xpath(xpath, root_element=None):
    """Decorated '_click_by_xpath()' call."""

    return _click_by_xpath(xpath, root_element=root_element)

def click_by_javascript(xpath, root_element=None):
    """
    Find the first element matching 'xpath' and 'root_element' and send '.click()' event to it
    using javascript.
    """

    root_element = _validate_root_element(xpath, root_element)
    element = find_by_xpath(xpath, root_element=root_element, many=False)
    get_driver().execute_script("arguments[0].click();", element)
    return element

@RepeatOnWebDriverException
def read_text_by_xpath(xpath, root_element=None, allow_empty=True):
    """
    Find the first element matching 'xpath' and 'root_element' and return its text. If
    'allow_empty' is 'False' and the text is empty, raise 'WebDriverException'.
    """

    root_element = _validate_root_element(xpath, root_element)
    text = _find_by_xpath(xpath, root_element, False).text
    if not text and allow_empty:
        raise WebDriverException(f"Text empty: '{xpath}'")
    return text

def _read_attribute_by_xpath(xpath, attribute, root_element=None):
    """
    Find the first element matching 'xpath' and 'root_element', call its method
    'get_attribute(<attribute>)' and return it. 'xpath' and 'root_element' are passed to
    'find_by_xpath()'.
    """

    root_element = _validate_root_element(xpath, root_element)
    element = _find_by_xpath(xpath, root_element=root_element, many=False)
    return element.get_attribute(attribute)

@RepeatOnWebDriverException
def read_attribute_by_xpath(xpath, attribute, root_element=None):
    """Decorated '_read_attribute_by_xpath()' call."""

    return _read_attribute_by_xpath(xpath, attribute, root_element=root_element)

@RepeatOnWebDriverException
def _send_keys_by_xpath(xpath, keys, root_element):
    """
    Find the first element matching 'xpath' and 'root_element' and try to change its value to
    'keys'. In case of failure, try again couple of times.
    """

    element = _find_by_xpath(xpath, root_element=root_element, many=False)
    element.clear()
    element.send_keys(keys)
    # Wait a brief moment so that the text can be seen. Useful for debugging.
    time.sleep(0.4)
    element_value = element.get_attribute("value")
    if element_value != keys:
        raise WebDriverException(f"Element's value does not match with sent keys:\n"
                                 f"'{element_value}' and '{keys}'")
    return element

def send_keys_by_xpath(xpath, keys, clear_first=True, root_element=None):
    """
    Find the first element matching 'xpath' and 'root_element' and try to change its value to
    either 'keys', or if 'clear_first' is 'True', append 'keys' to its value. In case of failure,
    try again couple of times.
    """

    if not isinstance(keys, str):
        keys = f"{keys}"

    root_element = _validate_root_element(xpath, root_element)
    if not clear_first:
        # Append 'keys' to original value.
        original_value = read_attribute_by_xpath(xpath, "value", root_element=root_element)
        keys = original_value + keys
    return _send_keys_by_xpath(xpath, keys, root_element)

def set_value(xpath, value):
    """Set value of the element matching 'xpath' to 'value'."""

    for _ in range(3):
        get_driver().execute_script(f"arguments[0].value='{value}';",
                                    find_by_xpath(xpath))
        if read_attribute_by_xpath(xpath, "value") == value:
            return
        time.sleep(1)
    raise WebDriverException

def get_current_url(driver=None):
    """Return current url as a string."""

    if not driver:
        driver = get_driver()
    return driver.current_url

def _open_url(url, refresh, driver):
    """
    Open the 'url'. Arguments are similar to the arguments in 'open_url()'. Return 'True' if the
    new page was opened, otherwise return 'False'.
    """

    is_different_url = get_current_url(driver=driver) != url
    if refresh or is_different_url:
        driver.get(url)
        return True
    return False

@contextmanager
def open_url(url, go_back=True, refresh=False, driver=None):
    """
    Open the 'url'. If 'go_back' is 'True', go back to the original url afterwards. If 'refresh' is
    'True', open the 'url' even if it is already open.

    Can be used like this:
    > with open_url("google.com"):
    >     print("Now at 'google.com'")
    > print("Now at starting url.")
    """

    _additional_page_opening_time = 1
    if not driver:
        driver = get_driver()

    # Save original URL for later.
    original_url = get_current_url(driver=driver)

    # Try to open the new URL.
    if _open_url(url, refresh, driver):
        time.sleep(_additional_page_opening_time)

    # Not handling exceptions here to make debugging easier.
    yield

    # Go back to the new URL if needed.
    if go_back and _open_url(original_url, refresh, driver):
        time.sleep(_additional_page_opening_time)

@RepeatOnNoAlertPresentException
def accept_alert():
    """Accept alert by clicking 'OK'."""

    time.sleep(1)
    verification_alert = get_driver().switch_to.alert
    verification_alert.accept()

@RepeatOnNoAlertPresentException
def cancel_alert():
    """Accept alert by clicking 'Cancel'."""

    time.sleep(1)
    verification_alert = get_driver().switch_to.alert
    verification_alert.dismiss()
