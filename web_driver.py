#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles initializing of '_WebDriver'."""

import os
import logging
from contextlib import suppress
from urllib3.exceptions import MaxRetryError

import selenium
from selenium.webdriver.remote.command import Command
from selenium.webdriver.chrome.options import Options

import session
import service

_MODULE_NAME, _ = os.path.splitext(os.path.basename(__file__))
_LOG = logging.getLogger(name=_MODULE_NAME)

def _get_default_options():
    """Return the default options for a new driver."""

    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("disable-infobars")
    return options

class _WebDriver(selenium.webdriver.remote.webdriver.WebDriver):
    """Remote driver class that uses an existing session when possible."""

    def __init__(self, options, port, session_id=None):
        """Initialize '_WebDriver'."""

        if not isinstance(options, Options):
            raise TypeError(f"Invalid type: {type(options)}")

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

def get_driver():
    """Return instance of '_WebDriver' and start the 'chromedriver' service if needed."""

    # Use the default port if custom port is not found in environment.
    service._start_chromedriver()

    options = _get_default_options()
    port = os.environ.get(service.PORT_ENV_KEY, service.DEFAULT_PORT)
    session_id = session._read_session_id()

    with suppress(selenium.common.exceptions.WebDriverException):
        driver = _WebDriver(options, port, session_id=session_id)
        session._save_session_id(driver.session_id)
        return driver

    session._clear_session_id()

    driver = _WebDriver(options, port)
    session._save_session_id(driver.session_id)
    return driver

def shutdown():
    """Shutdown the 'chromedriver' service."""

    session._clear_session_id()
    service._shutdown_chromedriver()
