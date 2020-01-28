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

class ServiceError(Exception):
    """Custom exception for when 'chromedriver' service is not running or cannot be found."""

class _WebDriver(selenium.webdriver.remote.webdriver.WebDriver):
    """Remote driver class that uses an existing session when possible."""

    def __init__(self, port, options=None, session_id=None):
        """Initialize '_WebDriver'."""

        if not options:
            options = _get_default_options()
        assert isinstance(options, Options)

        self._saved_session_id = session_id

        command_executor = f"http://127.0.0.1:{port}"
        _LOG.debug(f"Using 'command_executor': '{command_executor}'")

        try:
            super().__init__(command_executor=command_executor, desired_capabilities={},
                             options=options)
        except MaxRetryError:
            raise ServiceError("chromedriver service not running")

    def execute(self, driver_command, params=None):
        """Override 'super().execute()' so existing session is used."""

        if driver_command == Command.NEW_SESSION and self._saved_session_id:
            return {"success": 0, "value": None, "sessionId": self._saved_session_id}
        return super().execute(driver_command, params=params)

def get_driver():
    """Return instance of '_WebDriver' and start the 'chromedriver' service if needed."""

    # Use the default port if custom port is not found in environment.
    service._start_chromedriver()

    port = os.environ.get(service.PORT_ENV_KEY, service.DEFAULT_PORT)
    session_id = session._read_session_id()

    with suppress(selenium.common.exceptions.WebDriverException):
        driver = _WebDriver(port, session_id=session_id)
        _ = driver.current_url
        session._save_session_id(driver.session_id)
        _LOG.debug(f"Using session ID: {driver.session_id}")
        return driver

    _LOG.warning("Resetting web driver because of invalid session ID")
    session._clear_session_id()

    driver = _WebDriver(port)
    session._save_session_id(driver.session_id)
    return driver

def shutdown():
    """Shutdown the 'chromedriver' service."""

    session._clear_session_id()
    service._shutdown_chromedriver()