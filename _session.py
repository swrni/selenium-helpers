#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script handles reading and saving of the session ID, used by 'WebDriver'."""

import os
import logging

_SESSION_ID_ENV_KEY = "CHROMEDRIVER_SESSION_ID"

_MODULE_NAME, _ = os.path.splitext(os.path.basename(__file__))
_LOG = logging.getLogger(name=_MODULE_NAME)

class SessionAlreadyExists(Exception):
    """Custom exception for when the session ID is already in environment."""

    def __init__(self, *args, **kwargs):
        """Initialize 'SessionAlreadyExists'."""

        super().__init__(*args, **kwargs)

def _read_session_id():
    """
    Return the session ID that is currently used in chromedriver. Return 'None' if it is not
    defined in environment.
    """

    return os.environ.get(_SESSION_ID_ENV_KEY, None)

def _save_session_id(session_id):
    """Add the 'session_id' to environment. Raise 'SessionAlreadyExists' if it is already defined."""

    if _SESSION_ID_ENV_KEY in os.environ:
        if os.environ[_SESSION_ID_ENV_KEY] == session_id:
            _LOG.info("Session ID already in environment: '%s'", session_id)
            return
        raise SessionAlreadyExists(f"'_SESSION_ID_ENV_KEY' is already defined: "
                                   f"'{os.environ[_SESSION_ID_ENV_KEY]}'")
    os.environ[_SESSION_ID_ENV_KEY] = session_id

def _clear_session_id():
    """Remove session ID from the environment."""

    if _SESSION_ID_ENV_KEY in os.environ:
        del os.environ[_SESSION_ID_ENV_KEY]
