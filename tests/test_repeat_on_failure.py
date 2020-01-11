#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Author: Henri Immonen <henri.immonen@mostdigital.fi>

"""Tests for 'repeat_on_failure'."""

from repeat_on_failure import ReTry

tests = []

# Case 1.
tries = 0
@ReTry(Exception, sleep_time=0, tries=5)
def case1(item):
    global tries
    if tries < 3:
        tries += 1
        raise Exception("failure")
    print(f"Printing item: '{item}'")

def test_case1():
    print("Starting 'test_case1'.")
    case1("A")
    print("'test_case1' done.")

tests.append(test_case1)

# Case 2.
tries = 0
@ReTry(Exception, sleep_time=0, tries=5)
def case2(item):
    global tries
    if tries < 3:
        tries += 1
        raise Exception("failure")
    print(f"Printing item: '{item}'")

def test_case2():
    print("Starting 'test_case2'.")
    try:
        case2("B")
    except Exception:
        pass
    print("'test_case2' done.")

tests.append(test_case2)

# Case 3.
class CustomException3(Exception):
    pass

tries = 0
@ReTry(CustomException3, sleep_time=0, tries=5)
def case3(item):
    global tries
    if tries < 3:
        tries += 1
        raise CustomException3("failure")
    print(f"Printing item: '{item}'")

def test_case3():
    print("Starting 'test_case3'.")
    case3("B")
    print("'test_case3' done.")

tests.append(test_case3)

# Case 4.
class CustomException4(Exception):
    pass

tries = 0
@ReTry(CustomException4, sleep_time=0, tries=1)
def case4(item):
    global tries
    if tries < 4:
        tries += 1
        raise CustomException4("failure")
    print(f"Printing item: '{item}'")

def test_case4():
    print("Starting 'test_case4'.")
    try:
        case4("B")
    except CustomException4:
        pass
    print("'test_case4' done.")

tests.append(test_case4)

# Run tests.
for test in tests:
    test()