#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles initializing 'chromedriver' service."""

import os
import logging
import subprocess

# Define corresponding environment variable to point to 'chromedriver' executable.
PATH_ENV_KEY = "CHROMEDRIVER_PATH"

# Define corresponding environment variable to use custom port for the service.
PORT_ENV_KEY = "CHROMEDRIVER_PORT"
DEFAULT_PORT = "9515"

# Define corresponding environment variable to set the log level for the service.
LOG_LEVEL_ENV_KEY = "CHROMEDRIVER_LOG_LEVEL"
ALLOWED_LOG_LEVELS = ("ALL", "DEBUG", "INFO", "WARNING", "SEVERE", "OFF")
_DEFAULT_LOG_LEVEL = "WARNING"

# Define corresponding environment variable to set the log file for the service.
LOG_PATH_ENV_KEY = "CHROMEDRIVER_LOG_PATH"

_MODULE_NAME, _ = os.path.splitext(os.path.basename(__file__))
_LOG = logging.getLogger(name=_MODULE_NAME)

def _read_port():
    """
    Try reading port number from the environment, otherwise use the default value:
    'DEFAULT_PORT'.
    """

    if PORT_ENV_KEY not in os.environ:
        _LOG.info("Using default port: '%s'", DEFAULT_PORT)
        os.environ[PORT_ENV_KEY] = DEFAULT_PORT
    return os.environ[PORT_ENV_KEY]

def _read_log_path():
    """Try reading log path from the environment."""

    default_log_path = os.path.join(os.getcwd(), "service.log")
    log_path = os.environ.get(LOG_PATH_ENV_KEY, default_log_path)
    _LOG.info("Logging to file: '%s'", log_path)
    return log_path

def _read_log_level():
    """
    Try reading log level from the environment, otherwise use the default value:
    '_DEFAULT_LOG_LEVEL'.
    """

    if LOG_LEVEL_ENV_KEY not in os.environ:
        _LOG.info("Using default log level: '%s'", _DEFAULT_LOG_LEVEL)
        return _DEFAULT_LOG_LEVEL

    log_level = os.environ[LOG_LEVEL_ENV_KEY]
    if log_level in ALLOWED_LOG_LEVELS:
        return log_level

    _LOG.error("Unknown log level value: '%s'. Changing to the default: '%s'", log_level,
               _DEFAULT_LOG_LEVEL)
    return _DEFAULT_LOG_LEVEL

def _shutdown_chromedriver():
    """Shutdown the service."""

    _LOG.info("Shutting down chromedriver")
    subprocess.call("taskkill /f /im chromedriver.exe", stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

def _start_chromedriver():
    """Start chromedriver executable."""

    _LOG.info("Starting a new chromedriver instance")

    # Verify that the service is actually down before starting a new one.
    _shutdown_chromedriver()

    executable_path = os.environ[PATH_ENV_KEY]
    cmd = [executable_path,
           f"--port={_read_port()}",
           f"--log-path={_read_log_path()}",
           f"--log-level={_read_log_level()}",
           "--readable-timestamp"]
    subprocess.Popen(cmd)
