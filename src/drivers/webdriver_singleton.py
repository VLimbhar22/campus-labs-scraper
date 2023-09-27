from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome

DELAY = 1


class WebDriverSingleton:
    """
    Create a single instance of the webdriver
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

            # Set up Chrome WebDriver
            options = webdriver.ChromeOptions()
            options.page_load_strategy = 'none'
            chrome_path = ChromeDriverManager().install()
            chrome_service = Service(chrome_path)
            driver = Chrome(options=options, service=chrome_service)
            driver.implicitly_wait(DELAY)

            # Set up the webdriver
            cls._instance.driver = webdriver.Chrome()

        return cls._instance
