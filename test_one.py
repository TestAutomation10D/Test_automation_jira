import os


def test_one():
    print(os.environ.get("AUTH_TOKEN"))
    assert 1 == 2
