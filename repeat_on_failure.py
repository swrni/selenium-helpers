#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has helper functions for using Selenium."""

import sys
import time
from contextlib import contextmanager

# Number of tries before raising exception.
_TRIES = 4
# Time to sleep between tries, in seconds.
_SLEEP_TIME = 2

class RepeatOnFailure:
    """
    Class for repeating function execution if it raised a known exception. Can be used as
    decorator.
    """

    def __init__(self, tries=_TRIES, sleep_time=_SLEEP_TIME, exception_types=()):
        """
        Initialize 'RepeatOnFailure'. If exception is raised, try executing the function again
        'tries' times while sleeping 'sleep_time' seconds in between function calls. Exceptions
        which types are in 'exception_types' are handled, while others are re-raised.
        """

        self.tries = tries
        self.sleep_time = sleep_time
        self.exception_types = exception_types

    def __call__(self, function_with_params):
        """Call 'function_with_params' repeatedly on failure."""

        def try_to_execute(*args, **kwargs):
            """Pass arguments to 'function_with_params'."""

            for try_index in range(1, self.tries + 1):
                try:
                    return function_with_params(*args, **kwargs)
                except Exception as raised_exception:
                    # Catch all exceptions but re-raise exceptions which types are not in
                    # 'self.exception_types'.
                    handle_exception = any((isinstance(raised_exception, exception_type)
                                            for exception_type in self.exception_types))
                    # Re-raise unknown exceptions.
                    if not handle_exception:
                        raise
                    # Re-raise exception after 'self.tries'. 
                    if try_index == self.tries:
                        raise
                time.sleep(self.sleep_time)
            return None

        return try_to_execute

RepeatOnError = RepeatOnFailure(exception_types=(Exception, ))

@contextmanager
def repeat_on_exceptions(function_with_params, tries=_TRIES, sleep_time=_SLEEP_TIME,
                         exception_types=(), *args, **kwargs):
    """
    Try re-running 'function_with_params' in case it raises any of the exceptions in
    'exception_types'.
    """

    for try_index in range(1, tries + 1):
        try:
            yield function_with_params(*args, **kwargs)
        except Exception as raised_exception:
            # Catch all exceptions but re-raise exceptions which types are not in
            # 'exception_types'.
            handle_exception = any((isinstance(raised_exception, exception_type)
                                    for exception_type in exception_types))
            # Re-raise unknown exceptions.
            if not handle_exception:
                raise
            # Re-raise exception after 'tries'. 
            if try_index == tries:
                raise
        time.sleep(sleep_time)
    return None
