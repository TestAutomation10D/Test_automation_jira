import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def test_report_ext(driver):
    suite_board = (By.CSS_SELECTOR, '[href="#suites"]')
    test_metrics_board = (By.CSS_SELECTOR, '[href="#test-metrics"]')
    dashboard_pdf = (By.CSS_SELECTOR, '[id="download"] i')
    print_pdf_test_suite = (By.CSS_SELECTOR, '[class="fa fa-print"]')
    print_pdf_test_metrics = (By.XPATH, '(//*[@class="fa fa-print"])[2]')
    csv_suite = (By.CSS_SELECTOR, '[title="CSV"]')
    csv_test_metrics = (By.XPATH, '(//*[@title="CSV"])[2]')

    driver.get("file:////home/suryamr/jira_org/reports/year_2022/month_08/date_16/Test_report_2022_08_16_10_16_56.html")
    time.sleep(4)
    driver.execute_script("var a = document.querySelector('title'); a.innerText = 'SANITY REPORT'")
    driver.execute_script("""var a = document.querySelector('[class="header__title"]'); a.innerText = 'SANITY REPORT'""")
    driver.find_element(*dashboard_pdf).click()
    time.sleep(4)
    driver.find_element(*suite_board).click()
    driver.find_element(*csv_suite).click()
    # driver.find_element(*print_pdf_test_suite).click()
    time.sleep(5)
    driver.find_element(*test_metrics_board).click()
    driver.find_element(*csv_test_metrics).click()
    # driver.find_element(*print_pdf_test_metrics).click()
    time.sleep(4)
    driver.quit()
