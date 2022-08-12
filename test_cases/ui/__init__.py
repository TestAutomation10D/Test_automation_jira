import os
from datetime import datetime
from os.path import join
import requests
from ..document_creation import DocumentCreation
from dotenv import load_dotenv

jira_api_endpoint = ".atlassian.net/rest/api/2/issue"


class JiraClientInit:

    def get_timestamp(self):
        self.timestamp = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')

    def create_document_obj(self):
        self.doc = DocumentCreation()

    def insert_comment(self, comment):
        self.doc.create_para_object()
        self.doc.add_run_to_para_obj()
        self.doc.add_text_to_run_obj(comment)

    def save_image_to_doc(self, ticket_id):
        ticket_id = ticket_id.replace("-", "_")
        self.img_path = f"/jira_passed_images/{ticket_id}_images"
        img_path = self.img_path
        full_path = os.path.abspath(__file__).split("/ui")[0]
        if "jira_passed_images" not in os.listdir(path=full_path):
            os.makedirs(full_path+"/jira_passed_images")
        if f"{ticket_id}_images" not in os.listdir(path=full_path+"/jira_passed_images"):
            os.makedirs(f"{full_path}/jira_passed_images/{ticket_id}_images")
        self.get_timestamp()
        img_path = f"{img_path}/{ticket_id}_{self.timestamp}.png"
        self.driver.save_screenshot(full_path+img_path)
        self.doc.add_image_to_run_obj(full_path+img_path)

    def load_env_values(self):
        dotenv_path = join(os.path.abspath(__file__).split("/test_cases")[0], '.env')
        load_dotenv(dotenv_path)
        self.AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
        self.JIRA_DOMAIN = os.environ.get("JIRA_DOMAIN")
        self.PASS_STATUS_TRANSITION = os.environ.get("PASS_STATUS_TRANSITION")
        self.JIRA_CONDITION = os.environ.get("JIRA_CONDITION", None)

    def save_document_in_local(self, ticket_id):
        ticket_id = ticket_id.replace("-", "_")
        full_path = os.path.abspath(__file__).split("/ui")[0]
        doc_path = full_path + f"/jira_passed_docs/{ticket_id}_doc"
        if f"jira_passed_docs" not in os.listdir(path=full_path):
            os.makedirs(full_path+"/jira_passed_docs")
        if f"{ticket_id}_doc" not in os.listdir(path=full_path+"/jira_passed_docs"):
            os.makedirs(doc_path)
        doc_name = f"{ticket_id}_results_{self.timestamp}.docx"
        doc_path = doc_path+"/"+doc_name
        self.get_timestamp()
        self.doc.save_document(doc_path)
        return doc_path, doc_name

    def send_doc_to_jira(self, ticket_id, doc_path, doc_name):
        if self.JIRA_CONDITION:
            doc_url = f"https://{self.JIRA_DOMAIN}{jira_api_endpoint}/{ticket_id}/attachments"
            file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            files = [('file', (f'{doc_name}', open(f'{doc_path}', 'rb'), file_type))]
            headers = {
                'X-Atlassian-Token': 'no-check',
                'Authorization': f'Basic {self.AUTH_TOKEN}'
            }

            # Below post call is used to add the document on JIRA tickets
            # URL : https://testautomatejira.atlassian.net/rest/api/2/issue/{ticket_id}/attachments"
            requests.request("POST", doc_url, headers=headers, files=files)
