import os
import subprocess


def test_one():
    ff = open("env.txt", "r")
    print(ff.read())
    assert 1 == 2
