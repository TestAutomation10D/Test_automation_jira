import os
import requests
import json


def test_one():
    url = "https://testautomatejira.atlassian.net/rest/api/3/issue/TP-1"

    token = os.environ.get("AUTH_TOKEN")
    headers = {
        'Authorization': f"Basic {token}",
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)
    assert 1 == 2
