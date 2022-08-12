import time
import pytest
import logging
from selenium.webdriver.common.by import By
from . import JiraClientInit
import inspect


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class TestCaseJiraAddDoc(JiraClientInit):
    search_btn = (By.CSS_SELECTOR, 'input[type="search"]')
    product_name_label = (By.CSS_SELECTOR, 'h4[class="product-name"]')
    no_product_label = (By.CSS_SELECTOR, '[class="no-results"] h2')

    @pytest.fixture()
    def initialise(self, driver):
        self.driver = driver
        self.driver.get("https://rahulshettyacademy.com/seleniumPractise/#/")
        # create_document_obj is used to create a document object in init file to create local file
        self.create_document_obj()
        self.get_timestamp()
        self.load_env_values()

    @pytest.mark.parametrize("ticket_id", ["TP-1"])
    def test_search_with_valid_value_TP_1(self, ticket_id, initialise):
        search_value = "cau"
        self.driver.find_element(*self.search_btn).send_keys(search_value)
        case_name = inspect.getframeinfo(inspect.currentframe()).function
        self.insert_comment("Executing "+case_name+" test case")
        self.insert_comment(f"1. Inserted '{search_value}' value in search box")
        self.save_image_to_doc(ticket_id)
        self.insert_comment("2. Product Search filter is applied and result are shown")
        self.save_image_to_doc(ticket_id)
        product_name_text = self.driver.find_element(*self.product_name_label).text
        assert product_name_text == "Cauliflower - 1 Kg", "Product name is not matched"
        self.insert_comment("Result: Assertion condition is passed, Cauliflower - 1 Kg is found as product")
        self.save_image_to_doc(ticket_id)
        self.insert_comment("Test case Execution "+case_name+" is completed")
        doc_path, doc_name = self.save_document_in_local(ticket_id)
        self.send_doc_to_jira(ticket_id, doc_path, doc_name)

    # @pytest.mark.parametrize("ticket_id,search_value", [("TP-2", "cau")])
    # def test_search_with_valid_value_TP_2(self, ticket_id, search_value, initialise):
    #     input_value = search_value
    #     self.driver.find_element(*self.search_btn).send_keys(input_value)
    #     case_name = inspect.getframeinfo(inspect.currentframe()).function
    #     self.insert_comment("Executing " + case_name + " test case")
    #     self.insert_comment(f"1. Inserted '{search_value}' value in search box")
    #     self.save_image_to_doc(ticket_id)
    #     self.insert_comment("2. Product Search filter is applied and result are shown")
    #     self.save_image_to_doc(ticket_id)
    #     product_name_text = None
    #     try:
    #         product_name_text = self.driver.find_element(*self.no_product_label).text
    #         if product_name_text == "Sorry, no products matched your search!":
    #             assert False, "No products found for search value"
    #     except Exception as exp:
    #         if exp.__class__ == AssertionError:
    #             raise AssertionError("Assertion is not matched")
    #         else:
    #             pass
    #     if not product_name_text:
    #         assert True, "No products found for search value"
    #     self.insert_comment(f"Result: Assertion condition is passed, {search_value} is present as product filter")
    #     self.save_image_to_doc(ticket_id)
    #     self.insert_comment("Test case Execution " + case_name + " is completed")
    #     doc_path, doc_name = self.save_document_in_local(ticket_id)
    #     self.send_doc_to_jira(ticket_id, doc_path, doc_name)

    @pytest.mark.parametrize("ticket_id", ["TP-3"])
    def test_search_with_valid_value_TP_3(self, ticket_id, initialise):
        search_value = "bri"
        self.driver.find_element(*self.search_btn).send_keys(search_value)
        case_name = inspect.getframeinfo(inspect.currentframe()).function
        self.insert_comment("Executing " + case_name + " test case")
        self.insert_comment(f"1. Inserted '{search_value}' value in search box")
        self.save_image_to_doc(ticket_id)
        self.insert_comment("2. Product Search filter is applied and result are shown")
        self.save_image_to_doc(ticket_id)
        product_name_text = self.driver.find_element(*self.product_name_label).text
        assert product_name_text == "Brinjal - 1 Kg", "Product name is not matched"
        self.insert_comment("Result: Assertion condition is passed, Brinjal - 1 Kg is found as product")
        self.save_image_to_doc(ticket_id)
        self.insert_comment("Test case Execution " + case_name + " is completed")
        doc_path, doc_name = self.save_document_in_local(ticket_id)
        self.send_doc_to_jira(ticket_id, doc_path, doc_name)

    @pytest.mark.parametrize("ticket_id", ["TP-2"])
    def test_search_with_invalid_value_TP_2(self, ticket_id, initialise):
        search_value = "brdsffdasdfsi"
        self.driver.find_element(*self.search_btn).send_keys(search_value)
        product_name_text = self.driver.find_element(*self.no_product_label).text
        if product_name_text == "Sorry, no products matched your search!":
            assert False, "No products found for search value"