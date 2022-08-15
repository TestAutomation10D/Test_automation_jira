import os
import subprocess


def test_one():
    print(os.environ.get("AUTH_TOKEN"), "authtoken")
    # ff = open("env.txt", "r")
    # print(ff.read())
    assert 1 == 2
