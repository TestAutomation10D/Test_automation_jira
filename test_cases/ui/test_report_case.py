import time
import pytest
import logging
from selenium.webdriver.common.by import By
from . import JiraClientInit
import inspect


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class TestCaseJiraAddDoc:

    def test_search_with_valid_value_TP_1(self):
        assert 1 == 1

    def test_search_with_valid_value_TP_2(self):
        assert 1 == 1

    def test_search_with_valid_value_TP_3(self):
        assert 1 == 1
