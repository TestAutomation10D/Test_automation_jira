import os


def test_one():
    print(os.environ.get("TOKEN"))
    assert 1 == 2
