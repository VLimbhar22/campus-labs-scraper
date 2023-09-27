import time
import csv
import pickle
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from src.scrapers.xpaths import LOAD_MORE_BUTTON, CATEGORY_DROPDOWN, CATEGORY_CHECKBOX, PARENT_DIV

# Define file paths and constants
LINKS_FILE_PATH = 'src/input/links.txt'
OUTPUT_FILE_PATH = 'src/output/Organization_Information.csv'
LOG_FILE_PATH = 'src/logs/recheck_campus.txt'
PROGRESS_FILE_PATH = 'src/input/progress.pkl'
DELAY = 1

# Set up Chrome WebDriver
options = webdriver.ChromeOptions()
options.page_load_strategy = 'none'
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
driver = Chrome(options=options, service=chrome_service)
driver.implicitly_wait(DELAY)

# Initialize variables
output_writer = csv.writer(open(OUTPUT_FILE_PATH, 'a'))
progress_variables = pickle.load(open(PROGRESS_FILE_PATH, 'rb'))
current_organization = progress_variables['campus']
index = 0
