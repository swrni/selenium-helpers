#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Script has class 'ReTry' for repeating function execution in case of an error."""

import time

# Number of tries before raising exception.
_TRIES = 4
# Time to sleep between tries, in seconds.
_SLEEP_TIME = 2

class ReTry:
    """
    Class for repeating function execution if it raised a known type of an exception. Can be used
    as a decorator.
    """

    def __init__(self, exception, tries=_TRIES, sleep_time=_SLEEP_TIME):
        """
        Initialize 'ReTry'. If exception is raised, try executing the function again
        'tries' times while sleeping 'sleep_time' seconds in between function calls. Exception
        of type 'exception' is suppressed, while other exceptions are re-raised.
        """

        self.exception = exception
        self.tries = tries
        self.sleep_time = sleep_time

    def __call__(self, function_with_params):
        """Call 'function_with_params' repeatedly on failure."""

        def try_to_execute(*args, **kwargs):
            """Pass arguments to 'function_with_params'."""

            for try_count in range(self.tries + 1):
                try:
                    return function_with_params(*args, **kwargs)
                except self.exception:
                    if try_count == self.tries:
                        raise
                time.sleep(self.sleep_time)
            # We will never land here.

        return try_to_execute
