import os
import subprocess


def test_one():
    print("token="+repr(os.environ.get("AUTH_TOKEN").split(" ")), "authtoken")
    # ff = open("env.txt", "r")
    # print(ff.read())
    assert 1 == 2
