''' Bare-bones test to see if package(s) can be discovered '''
from example_package.example import add_one


def test_add_one():
    assert add_one(1) == 2
