import time
import pytest
import logging
from selenium.webdriver.common.by import By
from . import JiraClientInit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class TestCaseJiraAddDoc:

    @pytest.mark.parametrize("ticket_id", ["LB-1"])
    def test_search_with_valid_value_1(self, ticket_id):
        assert 1 == 1

    @pytest.mark.parametrize("ticket_id", ["TP-1"])
    def test_search_with_valid_value_3(self, ticket_id):
        assert 1 == 1

    @pytest.mark.parametrize("ticket_id", ["LB-2"])
    def test_search_with_valid_value_2(self, ticket_id):
        assert 1 == 1

    @pytest.mark.parametrize("ticket_id", ["TP-2"])
    def test_search_with_valid_value_4(self, ticket_id):
        assert 1 == 2

    @pytest.mark.parametrize("ticket_id", ["LB-6"])
    def test_search_with_valid_value_5(self, ticket_id):
        assert 1 == 2