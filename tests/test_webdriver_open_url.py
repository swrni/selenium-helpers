#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""A test for opening instances of '_WebDriver' class."""

import os
import logging
import subprocess

import _service
from _web_driver import get_driver

import sys
import time

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
sleep_time = 1

# os.environ[_service.PORT_ENV_KEY] = "9515"
os.environ[_service.PATH_ENV_KEY] = "C:\\Users\\HenriImmonen\\chromedriver\\latest\\chromedriver.exe"

driver = get_driver()
driver.get("http://www.google.com")
time.sleep(sleep_time)

#
driver2 = get_driver()
driver2.get("http://www.youtube.com")
time.sleep(sleep_time)

get_driver().close()
