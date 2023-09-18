import time


import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from xpaths import XPATHS


LINKS_FILE_PATH = 'links.txt'

# start by defining the options
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # it's more scalable to work in headless mode
# normally, selenium waits for all resources to download
# we don't need it as the page also populated with the running javascript code.
options.page_load_strategy = 'none'
# this returns the path web driver downloaded
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
# pass the defined options and service objects to initialize the web driver
driver = Chrome(options=options, service=chrome_service)
driver.implicitly_wait(5)


# Driver level operations
# Wait till the page is completely loaded
# Perform all scraping for one organization
# Move to next organization
links_file = open(LINKS_FILE_PATH, 'r')
for link in links_file.readlines():

    url = link.strip()
    driver.get(url)
    WebDriverWait(driver, 30)

    # Loop till all the organizations are loaded
    while True:
        try:
            load_more_button = driver.find_element(
                By.XPATH, XPATHS['Load More Button'])
            load_more_button.click()
        except NoSuchElementException:
            break

    # Category wise selection
    driver.find_element(By.XPATH, XPATHS['Category Dropdown'])

    # Store all the categories and their corresponding Xpaths
    categories = {}
    category_iterator = 1
    while True:
        try:
            driver.find_element(By.XPATH, f"{XPATHS['Category Checkbox']}")
            # TODO
        except NoSuchElementException:
            break


# Page level operations
# Load the page until all organizations are loaded (keep clicking click more while it exists)
# scrape the page
# Institution page - Scrape Links to organizations, logo, heading and short description
# Organization page - Scrape the long description, other information, social media links, and the contact information.


# Category level operations
# Scrape all the categories and then select and deselect every category
