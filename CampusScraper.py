import time
import csv
import pickle
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from src.scrapers.xpaths import LOAD_MORE_BUTTON, CATEGORY_DROPDOWN, CATEGORY_CHECKBOX, PARENT_DIV


class WebScraper:
    def __init__(self):
        self.DELAY = 1
        self.driver = self._initialize_driver()
        self.output_writer = csv.writer(open('src/output/Organization_Information.csv', 'a'))
        self.progress_variables = self._load_progress()
        self.current_organization = self.progress_variables['campus']
        self.index = 0

    def _initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'none'
        chrome_path = ChromeDriverManager().install()
        chrome_service = Service(chrome_path)
        driver = Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(self.DELAY)
        return driver

    def _load_progress(self):
        try:
            progress_file = open('src/input/progress.pkl', 'rb')
            return pickle.load(progress_file)
        except FileNotFoundError:
            return {'campus': 0}

    def _save_progress(self):
        self.progress_variables['campus'] = self.index - 1
        with open('src/input/progress.pkl', 'wb') as f:
            pickle.dump(self.progress_variables, f)

    def scrape(self):
        try:
            for link in open('src/input/links.txt', 'r').readlines():
                self.index += 1

                if self.index < self.current_organization:
                    continue

                url = link.strip()
                self.driver.get(url)
                time.sleep(max(self.DELAY, 10))

                # Load all organizations
                while True:
                    try:
                        load_more_button = self.driver.find_element(By.XPATH, LOAD_MORE_BUTTON)
                        load_more_button.click()
                        time.sleep(self.DELAY)
                    except (NoSuchElementException, ElementClickInterceptedException):
                        break

                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                    time.sleep(self.DELAY)

                    # Category wise selection
                    self.driver.find_element(By.XPATH, CATEGORY_DROPDOWN).click()

                    # Store all the categories and their corresponding XPATHS
                    self.categories = {}
                    self.category_iterator = 1
                    first_category = self.driver.find_element(By.XPATH, CATEGORY_CHECKBOX)
                    following_categories = first_category.find_elements(By.XPATH, "following-sibling::*")
                    first_category_name = first_category.text
                    first_category_checkbox = first_category.find_element(By.TAG_NAME, 'input')

                    all_names = [category.text for category in following_categories]
                    all_names = [first_category_name] + all_names

                    all_checkboxes = [category.find_element(By.TAG_NAME, 'input') for category in following_categories]
                    all_checkboxes = [first_category_checkbox] + all_checkboxes

                    all_categories_links = {}

                    for name, checkbox in zip(all_names, all_checkboxes):
                        all_categories_links[name] = []
                        checkbox.click()
                        time.sleep(self.DELAY)
                        parent_div = self.driver.find_element(By.XPATH, PARENT_DIV)
                        category_wise_organization_links = parent_div.find_elements(By.TAG_NAME, 'a')
                        current_link = link[:link.rindex('/')]
                        for org_link in category_wise_organization_links:
                            self.output_writer.writerow([name, org_link.get_attribute('href')])
                        checkbox.click()
                        time.sleep(self.DELAY)

        except Exception as e:
            with open('src/logs/recheck_campus.txt', 'a') as f:
                f.write(link)

        finally:
            self._save_progress()


if __name__ == '__main__':
    scraper = WebScraper()
    scraper.scrape()
