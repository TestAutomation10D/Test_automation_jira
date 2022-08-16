from selenium.webdriver.common.by import By


class TestUISanity:

    def test_two_sanity(self, driver):
        driver.get("https://rahulshettyacademy.com/AutomationPractice/")
        input_box = (By.CSS_SELECTOR, '[placeholder="Type to Select Countries"]')
        checkbox = (By.CSS_SELECTOR, '[id="checkBoxOption2"]')

        driver.find_element(*input_box).send_keys("india")
        driver.find_element(*checkbox).click()
