import copy
import logging
import os
import sys
import time
from datetime import datetime
from os.path import join, dirname
import json
import pytest
import requests
from dotenv import load_dotenv
from selenium.webdriver import Chrome, Firefox, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.firefox.options import Options as firefox_options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from pytest_html_reporter import attach
from .document_creation import DocumentCreation
from .jira_integration import JiraIntegration

logger = None
pytest_id = []
pytest_status = []
pytest_id_value = None
env_vars = {}
testcase_comment = None
img_path = None
jira_api_endpoint = ".atlassian.net/rest/api/2/issue"
main_file_path_report = None
result_value = "0"


def pytest_cmdline_main(config):
    """
        This method is to override the pytest configuration
        By overriding path variable, we can set the report generation in customized folder.
        The report file name based on timestamp value to distinguish the latest report file
        For eg:
            report file path = reports/<year>/<month>/<date>/
            report file name = test_report_<timestamp>.html
    """
    global main_file_path_report

    report_time = datetime.now()
    year = datetime.strftime(report_time, '%Y')
    month = datetime.strftime(report_time, '%m')
    date = datetime.strftime(report_time, '%d')
    timestamp = datetime.strftime(report_time, '%Y_%m_%d_%H_%M_%S')
    get_env_values()
    # If "REPORT_NAME" is mentioned on execution, report file will be generated based on proper given name
    report_name = os.environ.get("REPORT_NAME", "Test_report")
    pr_number = os.environ.get("GIT_PR_NUMBER", None)
    if report_name.capitalize() != "Test_report":
        report_name = check_and_modify_report_name(report_name)
    main_file_path_report = f"./reports/year_{year}/month_{month}/date_{date}/{report_name}_{timestamp}"
    if pr_number:
        report_name += "_pr_no_" + pr_number
    main_file_path_report += f"/{report_name.capitalize()}_{timestamp}.html"
    config.option.path = main_file_path_report


def check_and_modify_report_name(report_name):
    replace_name = report_name
    for n in ["/", "~", ")", "(", "!", "@", "#", "$", "^", "*", "=", ";", ":", "?", "]", "[", "{", "}", "|"]:
        replace_name = replace_name.replace(n, "_")
    return replace_name


def pytest_configure(config):
    """
        Pytest configure method is used to configure
        all the pre-conditions of pytest run.
    """
    global logger

    try:
        level = config.getoption('log-level'),
    except ValueError as e:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        if log_level.upper() == 'DEBUG':
            level = logging.DEBUG
        else:
            level = logging.INFO

    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def driver():
    global driver
    global url

    browser = os.environ.get('BROWSER') if "BROWSER" in os.environ else "firefox"
    mode = os.environ.get('HEADLESS') if "HEADLESS" in os.environ else None
    if browser.lower() == "firefox":
        ff_options = firefox_options()
        # To prevent download dialog for save as PDF
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)  # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        report_path = main_file_path_report.split("/")
        report_path = main_file_path_report.replace(report_path[len(report_path) - 1], "")[1:]
        profile.set_preference('browser.download.dir', os.getcwd() + report_path + "downloaded_files/")
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/plain,application/pdf')
        profile.set_preference('print.always_print_silent', True)
        profile.set_preference("pdfjs.disabled", True)
        if str(mode) == "True":
            ff_options.headless = True
        driver = Firefox(executable_path=GeckoDriverManager().install(), options=ff_options, firefox_profile=profile)
    else:
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')
        if str(mode) == "True":
            chrome_options.add_argument('--headless')
        driver = Chrome(ChromeDriverManager().install(), options=chrome_options)

    if "url" in os.environ:
        url = os.environ.get('url')
        driver.get(url)

    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def pytest_collection_modifyitems(session, config, items):
    """
    This hook is called after all tests have been collected.
    We can modify that list.
    """
    global pytest_id, pytest_id_value

    for pytest_test in copy.copy(items):
        if hasattr(pytest_test, 'callspec') and 'ticket_id' in pytest_test.callspec.params:
            pytest_id.append(str(pytest_test.callspec.params['ticket_id']))

    pytest_id_value = get_pytest_id(len(pytest_id))


def get_env_values():
    global env_vars

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    env_vars = {
        "AUTH_TOKEN": os.environ.get("AUTH_TOKEN", None),
        "JIRA_PROJECT_NAME": os.environ.get("JIRA_PROJECT_NAME", None),
        "PASS_STATUS_TRANSITION": os.environ.get("PASS_STATUS_TRANSITION", None),
        "JIRA_DOMAIN": os.environ.get("JIRA_DOMAIN", None),
        "FAIL_STATUS_TRANSITION": os.environ.get("FAIL_STATUS_TRANSITION", None),
        "JIRA_CONDITION": os.environ.get("JIRA_CONDITION", None),
        "JIRA_GITHUB_TOOL": os.environ.get("JIRA_GITHUB_TOOL", None),
        "TC_FUNCTIONAL_EXECUTION": os.environ.get("TC_FUNCTIONAL_EXECUTION", None),
        "TC_INTEGRATION_EXECUTION": os.environ.get("TC_INTEGRATION_EXECUTION", None),
        "TC_SANITY_EXECUTION": os.environ.get("TC_SANITY_EXECUTION", None),
        "GIT_PR_NUMBER": os.environ.get("GIT_PR_NUMBER", None),
        "GIT_REPOSITORY_NAME": os.environ.get("GIT_REPOSITORY_NAME", None),
        "GIT_ORG_NAME": os.environ.get("GIT_ORG_NAME", None),
        "BRANCH_NAME": os.environ.get("BRANCH_NAME", None),
        "JQL_COLUMN_NAME": os.environ.get("JQL_COLUMN_NAME", None),
        "JQL_ISSUE_TYPE": os.environ.get("JQL_ISSUE_TYPE", None),
    }


@pytest.fixture(scope="session", autouse=True)
def setup_module():
    print("\n")
    logger.info("Running setup Method for SESSION")


@pytest.fixture(scope="session", autouse=True)
def teardown_module():
    print("\n")
    yield
    logger.info("Running teardown for SESSION")
    try:
        test_report_ext()
    except Exception as exp:
        print(exp, "Exporting results files is failed")
    env_vars["report_status"] = result_value
    if env_vars["JIRA_CONDITION"] == 'True':
        jira_obj = JiraIntegration(**env_vars)
        jira_obj.find_ticket_id_in_jira()
        jira_obj.make_build_status_comment()
        jira_obj.add_comment_to_ticket_id()
        jira_obj.make_transitions_to_ticket()


def test_report_ext():
    suite_board = (By.CSS_SELECTOR, '[href="#suites"]')
    test_metrics_board = (By.CSS_SELECTOR, '[href="#test-metrics"]')
    dashboard_pdf = (By.CSS_SELECTOR, '[id="download"] i')
    # print_pdf_test_suite = (By.CSS_SELECTOR, '[class="fa fa-print"]')
    # print_pdf_test_metrics = (By.XPATH, '(//*[@class="fa fa-print"])[2]')
    csv_suite = (By.CSS_SELECTOR, '[title="CSV"]')
    csv_test_metrics = (By.XPATH, '(//*[@title="CSV"])[2]')

    ff_options = firefox_options()
    # To prevent download dialog for save as PDF
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    report_path = main_file_path_report.split("/")
    report_path = main_file_path_report.replace(report_path[len(report_path) - 1], "")[1:]
    profile.set_preference('browser.download.dir', os.getcwd() + report_path + "downloaded_files/")
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/plain,application/pdf')
    profile.set_preference('print.always_print_silent', True)
    profile.set_preference("pdfjs.disabled", True)
    # ff_options.headless = False
    time.sleep(4)
    driver = Firefox(executable_path=GeckoDriverManager().install(), options=ff_options, firefox_profile=profile)
    driver.get("file:///"+os.getcwd()+main_file_path_report[1:])
    time.sleep(4)
    driver.execute_script("var a = document.querySelector('title'); a.innerText = 'SANITY REPORT'")
    driver.execute_script("""var a = document.querySelector('[class="header__title"]'); a.innerText = 'SANITY REPORT'""")
    driver.find_element(*dashboard_pdf).click()
    time.sleep(2)
    driver.find_element(*suite_board).click()
    driver.find_element(*csv_suite).click()
    time.sleep(3)
    driver.find_element(*test_metrics_board).click()
    driver.find_element(*csv_test_metrics).click()
    time.sleep(4)
    driver.quit()


def get_pytest_id(length):
    for i in range(length):
        yield pytest_id[i]


@pytest.mark.hookwrapper(tryfirst=True)
def pytest_runtest_makereport(item):
    """
    This is called as each test ends
    """
    outcome = yield
    result = outcome.get_result()

    # log_file = "test_results.log"
    # if result.when == "call" and JIRA_CONDITION:
    #     try:
    #         with open(log_file, "a") as f:
    #             f.write(result.nodeid + "   " + result.outcome + "   " + str(result.duration)+"\n")
    #         ticket_id = next(pytest_id_value)
    #         if ticket_id in result.nodeid:
    #             send_results_to_jira(result, ticket_id)
    #         elif ticket_id not in result.nodeid:
    #             ticket_id = f"{JIRA_PROJECT_NAME}"+(result.nodeid.replace("_", "-")).split(f"{JIRA_PROJECT_NAME}")[1][:-1]
    #             send_results_to_jira(result, ticket_id)
    #     except Exception as e:
    #         print("Error", e)
    #         pass
    collect_screenshot(item, result)


def collect_screenshot(item, report):
    """
    :param item: The result for all items
    :param report: The result object for the test
    """
    global result_value

    # For tests inside ui, when the test fails, automatically take a
    # screenshot and display it in the html report

    location = getattr(report, 'location', [])

    if report.outcome in ["failed"]:
        result_value = "1"

    if "ui" in location[0] and (report.when == 'call' or report.when == "setup"):
        if report.outcome in ["skipped", "failed"]:
            _capture_screenshot()


def _capture_screenshot():
    """
        This method is used to attach the screenshot on UI failures to HTML report file
    """

    error_msg = f'Unable to create screenshot'
    if driver:
        try:
            attach(data=driver.get_screenshot_as_png())
            # doc_path, ticket_id = save_failed_details_on_dir(report)
            # send_failed_doc_to_jira(ticket_id, doc_path)
        except Exception as e:
            logging.error(f'{error_msg}  Exception: f{str(e)}')
    else:
        logging.error(f'{error_msg}  Selenium driver not valid.')

# def save_failed_details_on_dir(report):
#     ticket_id = f"{JIRA_PROJECT_NAME}" + \
#                 (report.nodeid.replace("_", "-")).split(f"{JIRA_PROJECT_NAME}")[1][:-1]
#     report_time = datetime.now()
#     timestamp = datetime.strftime(report_time, '%Y_%m_%d_%H_%M_%S')
#     file_exact_path = os.path.abspath(__file__).split("/conftest.py")[0]
#     img_path = "jira_failed_images"
#     if img_path not in os.listdir(path=file_exact_path):
#         os.makedirs(file_exact_path+"/"+img_path)
#     img_path += f"/{ticket_id}_img_{timestamp}.png"
#     driver.save_screenshot(file_exact_path+"/"+img_path)
#     doc_path = create_document_for_failed_case(file_exact_path+"/"+img_path, ticket_id)
#     return doc_path, ticket_id
#
#
# def create_document_for_failed_case(path, ticket_id):
#     doc = DocumentCreation()
#     doc.create_para_object()
#     doc.add_run_to_para_obj()
#     doc.add_text_to_run_obj(f"TICKET ID - {ticket_id}")
#     doc.create_para_object()
#     doc.add_run_to_para_obj()
#     doc.add_text_to_run_obj("This ticket is failed at the Below point of execution")
#     doc.create_para_object()
#     doc.add_run_to_para_obj()
#     doc.add_text_to_run_obj("Screenshot :")
#     doc.add_image_to_run_obj(path)
#     doc_path = path.replace("jira_failed_images", "jira_failed_docs")
#     doc_path = doc_path.replace("_img_", "_doc_")
#     doc_path = doc_path.replace(".png", ".docx")
#     file_exact_path = os.path.abspath(__file__).split("/conftest.py")[0]
#     path = "jira_failed_docs"
#     if path not in os.listdir(path=file_exact_path):
#         os.makedirs(file_exact_path+"/"+path)
#     doc.save_document(doc_path)
#     return doc_path


# def send_failed_doc_to_jira(ticket_id, doc_path):
#     doc_url = f"https://{JIRA_DOMAIN}{jira_api_endpoint}/{ticket_id}/attachments"
#     file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#     timestamp = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M')
#     files = [('file', (f'{ticket_id}_failed_doc_result_at_{timestamp}.docx', open(f'{doc_path}', 'rb'), file_type))]
#     headers = {
#         'X-Atlassian-Token': 'no-check',
#         'Authorization': f'Basic {AUTH_TOKEN}'
#     }
#
#     # Below post call is used to add the document on JIRA tickets
#     # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/attachments"
#     requests.request("POST", doc_url, headers=headers, files=files)
