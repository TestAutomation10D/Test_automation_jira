import http
import json
import os
from os.path import join, dirname
import requests
from dotenv import load_dotenv
import ast


class JiraIntegration:
    def __init__(self,
                 AUTH_TOKEN=None,
                 JIRA_PROJECT_NAME=None,
                 JIRA_DOMAIN=None,
                 PASS_STATUS_TRANSITION=None,
                 FAIL_STATUS_TRANSITION=None,
                 JIRA_CONDITION=None,
                 JIRA_GITHUB_TOOL=None,
                 TC_FUNCTIONAL_EXECUTION=None,
                 TC_INTEGRATION_EXECUTION=None,
                 TC_SANITY_EXECUTION=None,
                 GIT_PR_NUMBER=None,
                 GIT_REPOSITORY_NAME=None,
                 GIT_ORG_NAME=None,
                 BRANCH_NAME=None,
                 JQL_COLUMN_NAME=None,
                 JQL_ISSUE_TYPE=None,
                 report_status=None):
        self.auth_token = AUTH_TOKEN
        self.jira_project_name = JIRA_PROJECT_NAME
        self.jira_domain = JIRA_DOMAIN
        self.pass_status_transition = PASS_STATUS_TRANSITION
        self.fail_status_transition = FAIL_STATUS_TRANSITION
        self.jira_condition = ast.literal_eval(JIRA_CONDITION)
        self.jira_github_tool = ast.literal_eval(JIRA_GITHUB_TOOL)
        self.tc_functional_execution = TC_FUNCTIONAL_EXECUTION
        self.tc_integration_execution = TC_INTEGRATION_EXECUTION
        self.tc_sanity_execution = TC_SANITY_EXECUTION
        self.git_pr_number = GIT_PR_NUMBER
        self.git_repository_name = GIT_REPOSITORY_NAME
        self.git_org_name = GIT_ORG_NAME
        self.branch_name = BRANCH_NAME
        self.jql_column_name = JQL_COLUMN_NAME
        self.jql_issue_type = JQL_ISSUE_TYPE
        self.jira_domain_ext = ".atlassian.net"
        self.headers = {
            'Authorization': f'Basic {self.auth_token}',
            'Content-Type': 'application/json'
        }
        self.report_status = report_status
        self.git_domain = "https://github.com/"
        self.issue_id = None
        self.build_status_dict = None
        self.pr_link = None
        self.build_status = None
        if "github" in self.git_domain:
            self.pr_link = f"{self.git_domain}{self.git_org_name}/{self.git_repository_name}/pull/{self.git_pr_number}"
        self.ticket_id = None
        self.ticket_total = None

    def find_ticket_id_in_jira(self):
        if self.jira_github_tool:
            self.search_for_ticket_id_using_pr_status()
        else:
            self.search_for_ticket_id_using_search_api_call()

    def search_for_ticket_id_using_pr_status(self):
        # Below GET call is used to GET JIRA tickets by executing the JQL query
        # URL : https://testautomatejira.atlassian.net/rest/api/2/search?jql=<JQL_QUERY>
        try:
            search_url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/search"
            search_jql_query = f'''project = "{self.jira_project_name}" AND statusCategory = "In Progress" AND status in ({self.jql_issue_type}) AND development[pullrequests].all > 0 ORDER BY updated DESC'''
            response = requests.request("GET", search_url, headers=self.headers, params={"jql": search_jql_query})
            self.ticket_total = (response.json())["total"]
            if self.ticket_total == 1:
                self.issue_id = (response.json())["issues"][0]["id"]
                self.ticket_id = (response.json())["issues"][0]["key"]
            else:
                self.issue_id = []
                self.ticket_id = []
                for i in range(0, len(self.ticket_total)):
                    self.issue_id.append((response.json())["issues"][i]["id"])
                    self.ticket_id.append((response.json())["issues"][i]["key"])
                count = 0
                # https://testautomatejira.atlassian.net/rest/dev-status/latest/issue/detail?issueId=<issue_id>&applicationType=GitHub&dataType=branch
                for id in range(0, len(self.issue_id)):
                    url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/dev-status/latest/issue/detail"
                    params = {
                        "issueId": self.issue_id[id],
                        "applicationType": "Github",
                        "dataType": "branch"
                    }
                    response = requests.request("GET", url, headers=self.headers, params=params)
                    if self.pr_link in str(response.json()):
                        pull_req_details = response.json()["detail"]["pullRequests"]
                        for pr in pull_req_details:
                            if self.pr_link in pr:
                                if "MERGED" in pr["status"]:
                                    if pr["source"]["branch"] == self.branch_name:
                                        count = 1
                                        break
                        if count == 1:
                            self.ticket_id = self.ticket_id[id]
                            self.issue_id = self.issue_id[id]
                            break
        except Exception as exp:
            print(exp)
            self.ticket_id = None
            self.issue_id = None

    def search_for_ticket_id_using_search_api_call(self):
        # Below GET call is used to GET JIRA tickets by executing the JQL query
        # URL : https://testautomatejira.atlassian.net/rest/api/2/search?jql=<JQL_QUERY>
        try:
            self.issue_id = None
            self.ticket_id = None
            search_url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/search"
            search_jql_query = f'''project = '{self.jira_project_name}' AND status in ({self.jql_issue_type}) AND "{self.jql_column_name}" ~ "{self.pr_link}" ORDER BY created DESC '''
            response = requests.request("GET", search_url, headers=self.headers, params={"jql": search_jql_query})
            self.ticket_total = (response.json())["total"]
            if self.ticket_total == 1:
                self.issue_id = (response.json())["issues"][0]["id"]
                self.ticket_id = (response.json())["issues"][0]["key"]
            elif self.ticket_total == 0:
                raise Exception("Ticket Not found")
            else:
                self.issue_id = []
                self.ticket_id = []
                for i in range(0, self.ticket_total):
                    self.issue_id.append((response.json())["issues"][i]["id"])
                    self.ticket_id.append((response.json())["issues"][i]["key"])
                index = ""
                count = 0
                for key in range(0, len(self.ticket_id)):
                    url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/issue/{self.ticket_id[key]}"
                    response = requests.request("GET", url, headers=self.headers)
                    if self.branch_name in str(response.json()):
                        index = self.ticket_id[key]
                        count += 1
                if count == 1:
                    url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/issue/{index}"
                    response = requests.request("GET", url, headers=self.headers)
                    if response.status_code == http.HTTPStatus.OK:
                        self.issue_id = (response.json())["id"]
                        self.ticket_id = (response.json())["key"]
                else:
                    pass
        except Exception as exp:
            print(exp)
            self.ticket_id = None
            self.issue_id = None

    def make_build_status_comment(self):
        self.build_status_dict = {"0": "Passed", "1": "Failed"}
        self.build_status = "Build is " + self.build_status_dict[str(self.report_status)] + f" For PR LINK : {self.pr_link}"

    def add_comment_to_ticket_id(self):
        comment_url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/issue/{self.ticket_id}/comment"
        payload = json.dumps({"body": self.build_status })

        # Below post call is used to add the comment on JIRA tickets
        # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/comment"
        requests.request("POST", comment_url, headers=self.headers, data=payload)

    def make_transitions_to_ticket(self):
        # Below post call is to make transition for the JIRA tickets
        # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/transitions"
        transition_url = f"https://{self.jira_domain}{self.jira_domain_ext}/rest/api/2/issue/{self.ticket_id}/transitions"
        self.apply_transition_to_jira_ticket(transition_url, self.report_status)

    def apply_transition_to_jira_ticket(self, transition_url, status):
        transition_payload = {}
        if status == "0":
            transition_payload = json.dumps({"transition": {"id": f"{self.pass_status_transition}"}})
        else:
            transition_payload = json.dumps({"transition": {"id": f"{self.fail_status_transition}"}})
        requests.request("POST", transition_url, headers=self.headers, data=transition_payload)


if __name__ == "__main__":
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    env_vars = {
        "AUTH_TOKEN": os.environ.get("AUTH_TOKEN", False),
        "JIRA_PROJECT_NAME": os.environ.get("JIRA_PROJECT_NAME", False),
        "PASS_STATUS_TRANSITION": os.environ.get("PASS_STATUS_TRANSITION", 0),
        "JIRA_DOMAIN": os.environ.get("JIRA_DOMAIN", False),
        "FAIL_STATUS_TRANSITION": os.environ.get("FAIL_STATUS_TRANSITION", 0),
        "JIRA_CONDITION": os.environ.get("JIRA_CONDITION", False),
        "JIRA_GITHUB_TOOL": os.environ.get("JIRA_GITHUB_TOOL", False),
        "TC_FUNCTIONAL_EXECUTION": os.environ.get("TC_FUNCTIONAL_EXECUTION", False),
        "TC_INTEGRATION_EXECUTION": os.environ.get("TC_INTEGRATION_EXECUTION", False),
        "TC_SANITY_EXECUTION": os.environ.get("TC_SANITY_EXECUTION", False),
        "GIT_PR_NUMBER": os.environ.get("GIT_PR_NUMBER", False),
        "GIT_REPOSITORY_NAME": os.environ.get("GIT_REPOSITORY_NAME", False),
        "GIT_ORG_NAME": os.environ.get("GIT_ORG_NAME", False),
        "BRANCH_NAME": os.environ.get("BRANCH_NAME", False),
        "JQL_COLUMN_NAME": os.environ.get("JQL_COLUMN_NAME", None),
        "JQL_ISSUE_TYPE": os.environ.get("JQL_ISSUE_TYPE", None),
        "report_status": "0",
    }
    test_obj = JiraIntegration(**env_vars)
    test_obj.find_ticket_id_in_jira()
    test_obj.make_build_status_comment()
    test_obj.add_comment_to_ticket_id()
    test_obj.make_transitions_to_ticket()
