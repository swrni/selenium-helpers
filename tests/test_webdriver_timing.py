#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""A test for opening instances of '_WebDriver' class."""

import os
import logging
import subprocess

import service
from web_driver import get_driver

import sys
import time

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

os.environ[service.PORT_ENV_KEY] = "9515"
os.environ[service.PATH_ENV_KEY] = "C:\\Users\\HenriImmonen\\chromedriver\\latest\\chromedriver.exe"

def timing_kwargs(number=1):
    return {"setup": "from web_driver import get_driver",
            "stmt": "_ = get_driver()",
            "number": 1}

import timeit

for index in range(10):
    print(f"{index}.: {timeit.timeit(**timing_kwargs())}")