import os
import time
import selenium_helpers

import logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

import service
os.environ[service.PATH_ENV_KEY] = "C:\\Users\\HenriImmonen\\chromedriver\\latest\\chromedriver.exe"

default_driver = selenium_helpers.get_default_driver()
driver = default_driver.driver
driver.get("http://www.google.com")
# time.sleep(2)

url = "http://the-internet.herokuapp.com/large"
start_time = time.time()
reads = []
with default_driver.open_url(url, go_back=False):
    print(f"At '{url}'")
    for i in range(150):
        tr = 1 + (i % 50)
        td = 51 - tr
        reads.append(default_driver.read_text_by_xpath(f"//*[@id=\"large-table\"]/tbody/tr[{tr}]/td[{td}]"))
print(f"Elapsed time: {time.time() - start_time}")
print(f"Couple of first read times: {reads[:7]}")

print("Done, closing in 2 seconds")
# alert = Alert(driver)
# print(alert)

time.sleep(2)
driver.close()