#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has helper functions for using Selenium."""

import os
import sys
import time
from contextlib import contextmanager

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import _web_driver
from repeat_on_failure import RepeatOnFailure

_DRIVER = None

def get_driver():
    """Cache and return the driver."""

    global _DRIVER
    if not _DRIVER:
        _DRIVER = _web_driver.get_driver()
    return _DRIVER

class InvalidXPath(Exception):
    """Custom exception for invalid xpath."""

    def __init__(self, *args, **kwargs):
        """Initialize 'InvalidXPath'."""

        super().__init__(*args, **kwargs)

def _validate_root_element(xpath, root_element):
    """
    Verify that 'xpath' and 'root_element' are valid and return validated 'root_element'. Otherwise
    raise 'InvalidXPath' exception.
    """

    if not root_element:
        root_element = get_driver()

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

find_by_xpath = RepeatOnFailure(exception_types=(WebDriverException, ))(_find_by_xpath)

def _click_by_xpath(xpath, root_element):
    """Find and click the first element matching 'xpath' and 'root_element'."""

    root_element = _validate_root_element(xpath, root_element)
    element = find_by_xpath(xpath, root_element=root_element, many=False)
    element.click()
    return element

click_by_xpath = RepeatOnFailure(exception_types=(WebDriverException, ))(_click_by_xpath)

@RepeatOnFailure(exception_types=(WebDriverException, ))
def read_text_by_xpath(xpath, root_element=None):
    """Find the first element matching 'xpath' and 'root_element' and return its text."""

    root_element = _validate_root_element(xpath, root_element)
    return _find_by_xpath(xpath, root_element, False).text

def _read_attribute_by_xpath(xpath, attribute, root_element=None):
    """
    Find the first element matching 'xpath' and 'root_element', call its method 'get_attribute(<attribute>)' and return it. 'xpath'
    and 'root_element' are passed to 'find_by_xpath()'.
    """

    root_element = _validate_root_element(xpath, root_element)
    element = _find_by_xpath(xpath, root_element=root_element, many=False)
    return element.get_attribute(attribute)

read_attribute_by_xpath = RepeatOnFailure(exception_types=(WebDriverException, ))(_read_attribute_by_xpath)

def read_value_by_xpath(xpath, root_element=None):
    """Shorthand for calling 'read_attribute_by_xpath(xpath, "value", ...)'."""

    # TODO:: Remove this function as it is not really needed.
    return _read_attribute_by_xpath(xpath, "value", root_element=root_element)

@RepeatOnFailure(exception_types=(WebDriverException, ))
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

    root_element = _validate_root_element(xpath, root_element)
    if not clear_first:
        # Append 'keys' to original value.
        original_value = read_attribute_by_xpath(xpath, "value", root_element=root_element)
        keys = original_value + keys
    return _send_keys_by_xpath(xpath, keys, root_element)

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