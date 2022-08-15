import os
import subprocess


def test_one():
    print(len(os.environ.get("AUTH_TOKEN")))
    print("token="+repr(os.environ.get("AUTH_TOKEN")))
    print(True)
    # ff = open("env.txt", "r")
    # print(ff.read())
    assert 1 == 2
