import time
import csv
import pickle

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import NoSuchElementException, \
    ElementClickInterceptedException

from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.common.by import By
from xpaths import LOAD_MORE_BUTTON, CATEGORY_DROPDOWN, CATEGORY_CHECKBOX, PARENT_DIV

LINKS_FILE_PATH = 'input/links.txt'
OUTPUT_FILE_PATH = 'output/Organization_Information.csv'
LOG_FILE_PATH = 'logs/recheck_campus.txt'
PROGRESS_FILE_PATH = 'input/progress.pkl'
DELAY = 1

# start by defining the options
options = webdriver.ChromeOptions()
# it's more scalable to work in headless mode
# options.add_argument('--headless=new')
# normally, selenium waits for all resources to download
# we don't need it as the page also populated with the running javascript code.
options.page_load_strategy = 'none'
# this returns the path web driver downloaded
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
# pass the defined options and service objects to initialize the web driver
driver = Chrome(options=options, service=chrome_service)

driver.implicitly_wait(DELAY)

# Driver level operations
# Wait till the page is completely loaded
# Perform all scraping for one organization
# Move to next organization
links_file = open(LINKS_FILE_PATH, 'r')
output_file = open(OUTPUT_FILE_PATH, 'a')
progress_file = open(PROGRESS_FILE_PATH, 'rb')

output_writer = csv.writer(output_file)
progress_variables = pickle.load(progress_file)
print(progress_variables)
current_organization = progress_variables['campus']
index = 0

try:
    for link in links_file.readlines():
        try:
            index += 1
            # Skip the organizations that have been read already
            if index < current_organization:
                continue

            url = link.strip()
            driver.get(url)
            time.sleep(DELAY)

            # try:
            #     myElem = WebDriverWait(driver, DELAY).until(
            #         EC.presence_of_element_located((By.XPATH, LOAD_MORE_BUTTON)))
            #     print(f"Page {link} is ready!")
            # except TimeoutException:
            #     print(f"Loading took too much time for {link}.")

            # Load all organizations

            while True:
                try:
                    load_more_button = driver.find_element(
                        By.XPATH, LOAD_MORE_BUTTON)
                    load_more_button.click()
                    time.sleep(DELAY)
                except (NoSuchElementException, ElementClickInterceptedException):
                    break

            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(DELAY)
            # Category wise selection

            driver.find_element(By.XPATH, CATEGORY_DROPDOWN).click()

            # Store all the categories and their corresponding XPATHS
            categories = {}
            category_iterator = 1
            first_category = driver.find_element(
                By.XPATH, CATEGORY_CHECKBOX)
            following_categories = first_category.find_elements(
                By.XPATH, "following-sibling::*")
            first_category_name = first_category.text
            first_category_checkbox = first_category.find_element(By.TAG_NAME, 'input')

            # get all the names of the categories
            all_names = [category.text for category in following_categories]
            all_names = [first_category_name] + all_names

            # Get all the checkboxes
            all_checkboxes = [category.find_element(
                By.TAG_NAME, 'input') for category in following_categories]
            all_checkboxes = [first_category_checkbox] + all_checkboxes

            all_categories_links = {}

            for name, checkbox in zip(all_names, all_checkboxes):
                all_categories_links[name] = []
                checkbox.click()
                time.sleep(DELAY)
                parent_div = driver.find_element(By.XPATH, PARENT_DIV)
                category_wise_organization_links = parent_div.find_elements(
                    By.TAG_NAME, 'a')
                current_link = link[:link.rindex('/')]
                for org_link in category_wise_organization_links:
                    output_writer.writerow([name, org_link.get_attribute('href')])
                checkbox.click()
                time.sleep(DELAY)
        except Exception as e:
            with open(LOG_FILE_PATH, 'a') as f:
                f.write(link)


except Exception:
    print(f'Error Occurred. Please restart. Last scraped index: {index}')
finally:
    progress_variables['campus'] = index - 1
    print('Current Progress: ', progress_variables)
    print(progress_variables)
    with open('input/progress.pkl', 'wb') as f:
        pickle.dump(progress_variables, f)
# Page level operations
# Load the page until all organizations are loaded (keep clicking click more while it exists)
# scrape the page
# Institution page - Scrape Links to organizations, logo, heading and short description
# Organization page - Scrape the long description, other information, social media links, and the contact information.
