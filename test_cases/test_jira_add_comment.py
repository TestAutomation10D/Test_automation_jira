import time

import pytest
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class TestCaseJiraAddComment:

    @pytest.mark.parametrize("ticket_id", ["TP-1"])
    @pytest.mark.xfail
    def test_ticket_TP_1(self, ticket_id):
        assert 1 == 2

    @pytest.mark.parametrize("ticket_id", ["TP-2"])
    def test_ticket_TP_2(self, ticket_id):
        assert 1 == 1

    @pytest.mark.parametrize("ticket_id", ["TP-3"])
    def test_ticket_TP_3(self, ticket_id):
        assert 1 == 1
