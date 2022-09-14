import os
from os.path import dirname, join
from .jira_integration import JiraIntegration
from dotenv import load_dotenv


class TestSendResultJira:
    def get_env_values(self):
        if not os.getenv('GITHUB_ENV') and ".env" in os.listdir():
            dotenv_path = join(dirname(__file__), '.env')
            load_dotenv(dotenv_path)
        self.env_vars = {
            "AUTH_TOKEN": os.environ.get("AUTH_TOKEN", None),
            "JIRA_PROJECT_NAME": os.environ.get("JIRA_PROJECT_NAME", None),
            "PASS_STATUS_TRANSITION": os.environ.get("PASS_STATUS_TRANSITION", None),
            "JIRA_DOMAIN": os.environ.get("JIRA_DOMAIN", None),
            "FAIL_STATUS_TRANSITION": os.environ.get("FAIL_STATUS_TRANSITION", None),
            "JIRA_CONDITION": os.environ.get("JIRA_CONDITION", False),
            "JIRA_GITHUB_TOOL": os.environ.get("JIRA_GITHUB_TOOL", False),
            "GIT_PR_NUMBER": os.environ.get("GIT_PR_NUMBER"),
            "GIT_REPOSITORY_NAME": os.environ.get("GIT_REPOSITORY_NAME"),
            "GIT_ORG_NAME": os.environ.get("GIT_ORG_NAME"),
            "BRANCH_NAME": os.environ.get("BRANCH_NAME"),
            "REPORT_STATUS": os.environ.get("REPORT_STATUS"),
            "REPORT_NAME": os.environ.get("REPORT_NAME"),
            "REPORT_PATH": os.environ.get("REPORT_PATH")
        }
        self.jira_obj = JiraIntegration(**self.env_vars)
        self.jira_obj.ticket_id = os.environ.get("JIRA_TICKET_ID")
        self.jira_obj.issue_id = os.environ.get("JIRA_ISSUE_ID")

    def test_post_result_to_jira(self):
        self.get_env_values()
        self.jira_obj.make_build_status_comment()
        self.jira_obj.add_comment_to_ticket_id()
        self.jira_obj.make_transitions_to_ticket()

