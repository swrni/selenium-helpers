#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles reading and saving of the session ID, used by 'WebDriver'."""

import os
import logging
from contextlib import suppress

from filelock import FileLock

_FILE_DIR = os.path.dirname(__file__)
_MODULE_NAME, _ = os.path.splitext(os.path.basename(__file__))
_LOG = logging.getLogger(name=_MODULE_NAME)

# Save 'chromedriver' 'pid' to this file.
_SESSION_ID_FILE_PATH = os.path.join(_FILE_DIR, "session-id.txt")

# Lock file for '_SESSION_ID_FILE_PATH'.
_SESSION_ID_FILE_PATH_LOCK = _SESSION_ID_FILE_PATH + ".lock"
class SessionAlreadyExists(Exception):
    """Custom exception for when the session ID is already defined."""

def _read_session_id():
    """Return the previously saved session ID."""

    with FileLock(_SESSION_ID_FILE_PATH_LOCK, timeout=15):
        with suppress(FileNotFoundError):
            with open(_SESSION_ID_FILE_PATH, "r") as session_id_file:
                return session_id_file.readline().strip()
    return ""

def _save_session_id(session_id):
    """
    Save 'session_id' to a file. Raise 'SessionAlreadyExists' if it is already defined.
    """

    if not isinstance(session_id, str):
        _LOG.warning("'session_id' is of wrong type: %s", type(session_id))
        session_id = f"{session_id}"

    with FileLock(_SESSION_ID_FILE_PATH_LOCK, timeout=15):
        with open(_SESSION_ID_FILE_PATH, "w") as session_id_file:
            session_id_file.write(session_id)

def _clear_session_id():
    """Clear the last used session ID."""

    with FileLock(_SESSION_ID_FILE_PATH_LOCK, timeout=15):
        with suppress(FileNotFoundError):
            os.remove(_SESSION_ID_FILE_PATH)
