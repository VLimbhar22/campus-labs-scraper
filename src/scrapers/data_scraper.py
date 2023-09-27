import sys

sys.path.append("src")

from loggers.campus_error_logger import CampusErrorLogger
from loggers.organization_error_logger import OrganizationErrorLogger
from progress.progress_saver import ProgressSaver
import time
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
import pandas as pd
from savers.data_saver import DataSaver
from .xpaths import LOAD_MORE_BUTTON, CATEGORY_DROPDOWN, CATEGORY_CHECKBOX, PARENT_DIV, DESCRIPTION
from selenium.webdriver.common.keys import Keys
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome

DELAY = 1


class DataScraper:
    """
    Class to scrape the data from the campuses and the organizations
    """

    def __init__(self):
        # Set up Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'none'
        chrome_path = ChromeDriverManager().install()
        chrome_service = Service(chrome_path)
        driver = Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(DELAY)
        self.driver = driver
        self.progress_saver = ProgressSaver(file_path='src/input/progress.pkl')
        self.campus_writer = DataSaver(csv_file_path='src/output/Organization_Information.csv')
        self.organization_writer = DataSaver(csv_file_path='src/output/Organization_Information_updated.csv')
        self.campus_error_logger = CampusErrorLogger('src/logs/recheck_campus.txt')
        self.organization_error_logger = OrganizationErrorLogger('src/logs/recheck_organization.csv')

    def _process_description(self, category, url):
        description = self.driver.find_element(By.XPATH, DESCRIPTION)

        name = ''
        logo = ''
        long_description = ''
        instagram = ''
        facebook = ''
        twitter = ''
        other = ''
        website = ''
        email = ''
        phone = ''
        linkedin = ''

        divs = description.find_elements(By.XPATH, './*')

        description_flag = False

        for div in divs:
            if div.tag_name == 'h2':
                description_flag = True
                continue
            elif not description_flag:
                name = div.text
                try:
                    img = div.find_element(By.TAG_NAME, 'img')
                    logo = img.get_attribute('src')
                except NoSuchElementException:
                    pass
            elif "Contact Information" in div.text:
                contact_info = div.text
                email_match = re.search(r'E: ([^\n]+)', contact_info)
                phone_match = re.search(r'P: ([0-9-.() +]+)', contact_info)

                if email_match:
                    email = email_match.group(1)

                if phone_match:
                    phone = phone_match.group(1)

                continue
            else:
                try:
                    anchors = div.find_elements(By.TAG_NAME, 'a')
                    for anchor in anchors:
                        site = anchor.get_attribute('href')
                        if 'instagram' in site:
                            instagram = site
                        elif 'facebook' in site:
                            facebook = site
                        elif 'twitter' in site:
                            twitter = site
                        elif 'linkedin' in site:
                            linkedin = site
                        elif website == '':
                            website = site
                        else:
                            other = site
                except NoSuchElementException:
                    pass
            if description_flag:
                long_description += div.text + '\n'

        self.organization_writer.save_to_csv(
            [category, name, url, logo, long_description, email, phone, website, linkedin, instagram,
             facebook,
             twitter, other])

    def scrape_organizations(self, file_path='src/output/Organization_Information.csv'):
        current_organization = 0
        current_link = ''

        input_df = pd.read_csv(file_path, header=None)
        input_df.drop_duplicates()
        organization_progress = self.progress_saver.get_organization_progress()
        category = ''

        try:
            for index, row in input_df.iterrows():
                current_organization = index
                current_link = row[1]
                category = row[0]

                try:
                    if index < organization_progress:
                        continue

                    category, url = row[0], row[1]

                    self.driver.get(url)
                    self._process_description(category, url)

                except Exception as e:
                    self.organization_error_logger.log_error([category, current_link], e)

        except Exception as e:
            self.organization_error_logger.log_error([category, current_link], e)

        finally:
            self.progress_saver.save_progress(org_count=current_organization)

    def scrape_campuses(self, links_file='src/input/links.txt'):
        current_link = ''
        current_campus = 0
        try:
            # Loop through links

            campus_progress = self.progress_saver.get_campus_progress()
            for index, link in enumerate(open(links_file, 'r').readlines()):
                current_link = link
                current_campus = index

                if index < campus_progress:
                    continue

                url = link.strip()
                self.driver.get(url)
                time.sleep(max(DELAY, 10))

                # Load all organizations
                while True:
                    try:
                        load_more_button = self.driver.find_element(By.XPATH, LOAD_MORE_BUTTON)
                        load_more_button.click()
                        time.sleep(DELAY)
                    except (NoSuchElementException, ElementClickInterceptedException):
                        break

                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(DELAY)

                # Category wise selection
                self.driver.find_element(By.XPATH, CATEGORY_DROPDOWN).click()

                # Store all the categories and their corresponding XPATHS
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
                    time.sleep(DELAY)
                    parent_div = self.driver.find_element(By.XPATH, PARENT_DIV)
                    category_wise_organization_links = parent_div.find_elements(By.TAG_NAME, 'a')
                    current_link = link[:link.rindex('/')]
                    for org_link in category_wise_organization_links:
                        self.campus_writer.save_to_csv([name, org_link.get_attribute('href')])

                    checkbox.click()
                    time.sleep(DELAY)

        except Exception as e:
            self.campus_error_logger.log_error(current_link, e)

        finally:
            self.progress_saver.save_progress(campus_count=current_campus)
