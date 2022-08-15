import os
import subprocess


def test_one():
    auth_token = f"abcd {os.environ.get("TOKEN")}"
    print(os.environ.get("AUTH_TOKEN"))
    print(auth_token.replace(" ",""))
    # ff = open("env.txt", "r")
    # print(ff.read())
    assert 1 == 2
