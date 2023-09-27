import re
import pandas as pd
import pickle

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.scrapers.xpaths import DESCRIPTION

LINKS_FILE_PATH = 'src/output/Organization_Information.csv'
OUTPUT_FILE_PATH = 'src/output/Organization_Information_updated.csv'
LOG_FILE_PATH = 'src/logs/recheck_organization.txt'
DELAY = 1
PROGRESS_FILE_PATH = 'src/input/progress.pkl'

progress_file = open(PROGRESS_FILE_PATH, 'rb')

input_df = pd.read_csv(LINKS_FILE_PATH, header=None)
# orgs_df = pd.read_csv(OUTPUT_FILE_PATH, header=0)
orgs_df = pd.DataFrame()
input_df.drop_duplicates()

progress_variables = pickle.load(progress_file)
print(progress_variables)

current_index = progress_variables['organization']

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
new_data = []

try:
    for index, row in input_df.iterrows():
        try:
            if index < current_index:
                continue
            progress_variables['organization'] += 1
            category, url = row[0], row[1]

            driver.get(url)

            description = driver.find_element(By.XPATH, DESCRIPTION)
            name = ''
            logo = ''
            long_description = ''
            instagram = ''
            facebook = ''
            twitter = ''
            other = ''
            website = ''
            contact_info = ''
            email = ''
            phone = ''
            linkedin = ''

            i = 0
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

            new_data.append(
                [category, name, url, logo, long_description, email, phone, website, linkedin, instagram, facebook,
                 twitter, other])
        except Exception as e:
            with open(LOG_FILE_PATH, 'a') as f:
                f.write(row[1]+'\n')



except Exception as e:
    print(f'Error Occurred. Please restart.')
finally:
    progress_variables['organization'] -= 1
    orgs_df = pd.concat([orgs_df, pd.DataFrame(new_data)])
    orgs_df.to_csv(OUTPUT_FILE_PATH)
    print('Current Progress: ', progress_variables)
    with open('src/input/progress.pkl', 'wb') as f:
        pickle.dump(progress_variables, f)
