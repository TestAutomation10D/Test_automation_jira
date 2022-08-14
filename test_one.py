import os
import subprocess


def test_one():
    out_file = open("BCD.TXT", "w")
    sub = subprocess.call(['sed', 's/\"//g', os.environ.get("TOKEN")], stdout=out_file)
    print(sub)
    assert 1 == 2
