import copy
import logging
import os
from datetime import datetime
from os.path import join, dirname
import json
import pytest
import requests
from dotenv import load_dotenv
from selenium.webdriver import Chrome, Firefox, ChromeOptions
from selenium.webdriver.firefox.options import Options as firefox_options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from pytest_html_reporter import attach
from .document_creation import DocumentCreation


logger = None
pytest_id = []
pytest_status = []
pytest_id_value = None
AUTH_TOKEN = None
JIRA_DOMAIN = None
PASS_STATUS_TRANSITION = None
FAIL_STATUS_TRANSITION = None
JIRA_CONDITION = None
TEST_EXECUTION_NAME = None
CLIENT_ID = None
CLIENT_SECRET = None
TESTCASE_UPDATE = None
testcase_comment = None
img_path = None
project_key = {}
jira_api_endpoint = ".atlassian.net/rest/api/2/issue"
timestamp = ""


def pytest_cmdline_main(config):
    """
        This method is to override the pytest configuration
        By overriding path variable, we can set the report generation in customized folder.
        The report file name based on timestamp value to distinguish the latest report file
        For eg:
            report file path = ./reports/<year>/<month>/<date>/
            report file name = test_report_<timestamp>.html
    """
    global timestamp

    report_time = datetime.now()
    year = datetime.strftime(report_time, '%Y')
    month = datetime.strftime(report_time, '%m')
    date = datetime.strftime(report_time, '%d')
    timestamp = datetime.strftime(report_time, '%Y_%m_%d_%H_%M_%S')

    # If "REPORT_NAME" is mentioned on execution, report file will be generated based on proper given name
    report_name = os.environ.get('REPORT_NAME') if "REPORT_NAME" in os.environ else "Test_report"
    if report_name.capitalize() != "Test_report":
        report_name = check_and_modify_report_name(report_name)
    main_file_path_report = f"./reports/year_{year}/month_{month}/date_{date}/{report_name.capitalize()}_{timestamp}.html"
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

    browser = os.environ.get('BROWSER') if "BROWSER" in os.environ else "chrome"
    mode = os.environ.get('HEADLESS') if "HEADLESS" in os.environ else None
    if browser.lower() == "firefox":
        ff_options = firefox_options()
        if str(mode) == "True":
            ff_options.headless = True
        driver = Firefox(executable_path=GeckoDriverManager().install(), options=ff_options)
    else:
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
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
    get_env_values()


def get_env_values():
    global AUTH_TOKEN, JIRA_DOMAIN, PASS_STATUS_TRANSITION, FAIL_STATUS_TRANSITION, JIRA_CONDITION, CLIENT_ID, CLIENT_SECRET, TEST_EXECUTION_NAME, TESTCASE_UPDATE

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
    JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
    PASS_STATUS_TRANSITION = os.environ.get("PASS_STATUS_TRANSITION")
    FAIL_STATUS_TRANSITION = os.environ.get("FAIL_STATUS_TRANSITION")
    JIRA_CONDITION = os.environ.get("JIRA_CONDITION", None)
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    TEST_EXECUTION_NAME = os.environ.get("TEST_EXECUTION_NAME")
    TESTCASE_UPDATE = os.environ.get("TESTCASE_UPDATE")


def setup_module(module):
    print("\n")
    logger.info("Running setup for MODULE [%s]" % module.__name__)


def teardown_module(module):
    print("\n")
    logger.info("Running teardown for MODULE [%s]" % module.__name__)


def get_pytest_id(length):
    for i in range(length):
        yield pytest_id[i]


@pytest.mark.hookwrapper(tryfirst=True)
def pytest_runtest_makereport(item):
    """
    This is called as each test ends
    """
    global project_key

    outcome = yield
    result = outcome.get_result()

    log_file = "test_results.log"
    if result.when == "call":
        try:
            with open(log_file, "a") as f:
                ticket_id = next(pytest_id_value)
                f.write(result.nodeid + "   " + result.outcome + "   " + str(result.duration)+" Ticket ID - "+ticket_id+"\n")
                proj_key = ticket_id.split("-")[0]
            if JIRA_CONDITION:
                if proj_key in project_key.keys():
                    add_test_cases_in_test_execution(project_key[proj_key], ticket_id, result.outcome)
                else:
                    project_id = get_project_id(proj_key)
                    issue_type_id = get_issue_type_id(proj_key, TEST_EXECUTION_NAME)
                    test_exec_key = create_test_execution_ticket_in_jira(project_id, issue_type_id)
                    project_key[proj_key] = test_exec_key
                    add_test_cases_in_test_execution(project_key[proj_key], ticket_id, result.outcome)
        except Exception as e:
            print("Error occurred in making report", e)
            pass
    # collect_screenshot(item, result)


def get_authentication_token_for_xray_api():
    auth_cred = { "client_id": CLIENT_ID,"client_secret": CLIENT_SECRET }
    token = requests.request(url="https://xray.cloud.getxray.app/api/v1/authenticate", method="POST",
                     json=auth_cred)
    return json.loads(token.text)


def add_test_cases_in_test_execution(key, test_case_id, status):
    try:
        token = get_authentication_token_for_xray_api()
        headers = {"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json"}
        payload = {
        "testExecutionKey": key,
        "info": {
            "summary": f"Execution of automated tests at {timestamp}",
            "description": "This execution is automatically created when importing execution results from an external "
                           "source",
        },
        "tests": [
                {
                "testKey": test_case_id,
                "comment": "Successful execution" if status == "passed" else "Execution failed",
                "status": status.upper()
                }
            ]
        }
        requests.request(url="https://xray.cloud.xpand-it.com/api/v1/import/execution", method="POST", headers=headers,
                         json=payload, verify=False)
        if TESTCASE_UPDATE:
            send_results_to_jira(status, test_case_id, key)
    except Exception as e:
        logger.info("Exception occured when linking test case to test execution", e)


def create_test_execution_ticket_in_jira(project_id, issue_type_id, summary="Automated Test Execution summary",
                                         description="Description of the Test Execution"):
    payload = {
    "fields": {
        "project": {
            "id": project_id
        },
        "summary": summary,
        "description": description,
        "issuetype": {
            "id": issue_type_id
            }
        }
    }
    headers = {"Authorization": f"Basic {AUTH_TOKEN}",
               "Content-Type": "application/json"}
    url = f"https://{JIRA_DOMAIN}{jira_api_endpoint}"
    response = requests.request(url=url, method="POST", json=payload, headers=headers)
    exec_ticket_info = json.loads(response.content)
    return exec_ticket_info['key']


def get_project_id(proj_key):
    """
    :param proj_key: Send ticket ID to get the project ID
    :return: Extract the result from jira to get the project ID
    """
    try:
        url = f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/2/project"
        headers ={"Authorization": f"Basic {AUTH_TOKEN}",
                  "Content-Type": "application/json"}
        response = requests.request(url=url, method="GET", headers=headers)
        for res in json.loads(response.content):
            if res['key'] == proj_key:
                return res['id']
    except Exception as e:
        logger.info("Error occured when getting project id")


def get_issue_type_id(proj_key, issue_type):
    """
    :param proj_key: Project ID to know about the project Details
    :param issue_type: Issue type to create a test execution ticket
    :return: Sends the Extract issue type value for jira ticket
    """
    try:
        url = f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/2/project/{proj_key}"
        headers = {"Authorization": f"Basic {AUTH_TOKEN}",
                   "Content-Type": "application/json"}
        response = requests.request(url=url, method="GET", headers=headers)
        issues = json.loads(response.content)
        if issues['issueTypes']:
            for issue in issues['issueTypes']:
                if issue['name'] == issue_type:
                    return issue['id']
        else:
            raise Exception("No issue types in response")
    except Exception as e:
        logger.info("Exception occurred in getting issue type value", e)


def send_results_to_jira(result, ticket_id, test_execution_id):
    global testcase_comment

    # If testcase_dict status is skipped, then it belongs to XFail condition, which got failed
    testcase_dict = {"passed": "Passed", "failed": "Failed", "skipped": "Xfailed"}

    testcase_comment = f"{ticket_id} - Testcase is " + str(testcase_dict[result]) + f" in Test execution ticket ID - {test_execution_id}\n"
    comment_url = f"https://{JIRA_DOMAIN}{jira_api_endpoint}/{ticket_id}/comment"

    payload = json.dumps({"body": testcase_comment})
    headers = {
        'Authorization': f'Basic {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Below post call is used to add the comment on JIRA tickets
    # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/comment"
    requests.request("POST", comment_url, headers=headers, data=payload)

    # Below post call is to make transition for the JIRA tickets
    # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/transitions"
    # transition_url = f"https://{JIRA_DOMAIN}{jira_api_endpoint}/{ticket_id}/transitions"
    # apply_transition_to_jira_tickets(transition_url, headers=headers, status=result)


def apply_transition_to_jira_tickets(transition_url, headers, status):
    method = "POST"
    if status == "passed":
        transition_payload_failed = json.dumps({"transition": {"id": f"{PASS_STATUS_TRANSITION}"}})
        requests.request(method, transition_url, headers=headers, data=transition_payload_failed)
    elif status in ["failed", "skipped"]:
        transition_payload_failed = json.dumps({"transition": {"id": f"{FAIL_STATUS_TRANSITION}"}})
        requests.request(method, transition_url, headers=headers, data=transition_payload_failed)


def collect_screenshot(item, report):
    """
    :param item: The result for all items
    :param report: The result object for the test
    """

    # For tests inside ui, when the test fails, automatically take a
    # screenshot and display it in the html report

    location = getattr(report, 'location', [])

    if "ui" in location[0] and (report.when == 'call' or report.when == "setup"):
        if report.outcome in ["skipped", "failed"]:
            _capture_screenshot(report)


def _capture_screenshot(report):
    """
        This method is used to attach the screenshot on UI failures to HTML report file
    """

    error_msg = f'Unable to create screenshot'
    if driver:
        try:
            attach(data=driver.get_screenshot_as_png())
            # if JIRA_CONDITION:
            #     doc_path, ticket_id = save_failed_details_on_dir(report)
            #     send_failed_doc_to_jira(ticket_id, doc_path)
        except Exception as e:
            logging.error(f'{error_msg}  Exception: f{str(e)}')
    else:
        logging.error(f'{error_msg}  Selenium driver not valid.')


# def save_failed_details_on_dir(report):
#     # ticket_id = f"{PREFIX_TICKET_VALUE}" + \
#     #             (report.nodeid.replace("_", "-")).split(f"{PREFIX_TICKET_VALUE}")[1][:-1]
#     ticket_id = ""
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
#
#
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


