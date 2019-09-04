#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles initializing of '_WebDriver'."""

import os
import logging
import subprocess

import _session
import _service

import selenium
from selenium.webdriver.chrome.options import Options

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

    def __init__(self, *args, **kwargs):
        """Initialize 'ServiceError'."""

        super().__init__(*args, **kwargs)

class _WebDriver(selenium.webdriver.remote.webdriver.WebDriver):
    """Remote driver class that uses an existing session when possible."""

    def __init__(self, port, options=None):
        """Initialize '_WebDriver'."""

        if not options:
            options = _get_default_options()
        assert isinstance(options, Options)

        command_executor = f"http://127.0.0.1:{port}"
        _LOG.debug(f"Using 'command_executor': '{command_executor}'")

        from urllib3.exceptions import MaxRetryError
        try:
            super().__init__(command_executor=command_executor, desired_capabilities={},
                             options=options)
            _session._save_session_id(self.session_id)
        except MaxRetryError:
            raise ServiceError("chromedriver service not running")

    def execute(self, driver_command, params=None):
        from selenium.webdriver.remote.command import Command
        if driver_command == Command.NEW_SESSION:
            session_id = _session._read_session_id()
            if session_id:
                return {"success": 0, "value": None, "sessionId": session_id}
        return super().execute(driver_command, params=params)

def get_driver():
    """Return instance of '_WebDriver' and start the 'chromedriver' service if needed."""

    # Use the default port if custom port is not found in environment.
    port = os.environ.get(_service.PORT_ENV_KEY, _service.DEFAULT_PORT)
    try:
        return _WebDriver(port)
    except ServiceError as error:
        _LOG.info("chromedriver is not running: %s", error)
    _service._start_chromedriver()
    return _WebDriver(port)

def shutdown():
    """Shutdown the 'chromedriver' service."""

    _session._clear_session_id()
    _service._shutdown_chromedriver()
