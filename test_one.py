import os
import subprocess


def test_one():
    print("token="+repr(os.environ.get("AUTH_TOKEN")))
    print(True)
    if os.environ.get("AUTH_TOKEN") == "c3VyeWEubXIramlyYTFAMTBkZWNvZGVycy5pbjpnRTByeFptRzBEalQ0SXo3TkU4YUYzM0Y=":
        print("ENV value checked")
    # ff = open("env.txt", "r")
    # print(ff.read())
    assert 1 == 2
