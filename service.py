#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles initializing 'chromedriver' service."""

import os
import signal
import logging
import subprocess
from contextlib import suppress

from filelock import FileLock

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

_FILE_DIR = os.path.dirname(__file__)
_MODULE_NAME, _ = os.path.splitext(_FILE_DIR)
_LOG = logging.getLogger(name=_MODULE_NAME)

# Save 'chromedriver' 'pid' to this file.
_PID_FILE_PATH = os.path.join(_FILE_DIR, "chromedriver-pid.txt")

# Lock file for '_PID_FILE_PATH'.
_PID_FILE_PATH_LOCK = _PID_FILE_PATH + ".lock"

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

def _read_pid():
    """
    Read and return 'pid' of the currently running 'chromedriver' from the text file
    '_PID_FILE_PATH'. If not found, return 'None'.
    """

    with open(_PID_FILE_PATH, "r") as pid_file:
        pid = pid_file.readline().strip()
    with suppress(ValueError):
        return int(pid)
    return None

def _shutdown_chromedriver():
    """Shutdown the service."""

    _LOG.info("Shutting down chromedriver")

    with FileLock(_PID_FILE_PATH_LOCK, timeout=15):
        if os.path.isfile(_PID_FILE_PATH):
            pid = _read_pid()
            if pid:
                with suppress(OSError):
                    os.kill(pid, signal.SIGTERM)
            os.remove(_PID_FILE_PATH)

def _start_chromedriver():
    """Start chromedriver executable."""

    # TODO:: Check if process with the saved PID exists.

    _LOG.info("Starting a new chromedriver instance")

    executable_path = os.environ[PATH_ENV_KEY]
    cmd = [executable_path,
           f"--port={_read_port()}",
           f"--log-path={_read_log_path()}",
           f"--log-level={_read_log_level()}",
           "--readable-timestamp"]

    with FileLock(_PID_FILE_PATH_LOCK, timeout=15):
        process = subprocess.Popen(cmd)
        if process.poll():
            _LOG.info("An instance of chromedriver is already running")
        else:
            with open(_PID_FILE_PATH, "w") as pid_file:
                pid_file.write(str(process.pid))
    return process
