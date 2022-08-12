import time
import pytest
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class TestCase:

    search_input = (By.CSS_SELECTOR, '[name="q"]')
    google_search_btn = (By.CSS_SELECTOR, '[name="btnK"]')

    def setup_method(self):
        self.driver = Chrome(ChromeDriverManager().install())
        self.driver.navigate().to("https://www.google.in")
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def test_open_google_webpage(self):
        self.driver.find_element(*self.search_input).send_keys("testing")
        self.driver.find_element(*self.google_search_btn).click()

    def teardown_method(self):
        self.driver.quit()

if __name__ == "__main__":
    triangle_function()