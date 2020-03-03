import os
import time
import selenium_helpers

import logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

import service
os.environ[service.PATH_ENV_KEY] = "C:\\Users\\HenriImmonen\\chromedriver\\latest\\chromedriver.exe"

driver = selenium_helpers.Driver()
# driver = default_driver.driver

driver.driver.get("http://www.google.com")

url = "http://the-internet.herokuapp.com/large"
with driver.open_url(url, go_back=False):
    tr, td = 1, 1
    print(driver.read_text_by_xpath(f"//*[@id=\"large-table\"]/tbody/tr[{tr}]/td[{td}]"))

# driver.close()