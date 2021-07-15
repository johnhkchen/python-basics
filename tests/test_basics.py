''' Super bare-bones test to make sure unit tests are discoverable'''


def add(a, b):
    ''' Simple function to add two values '''
    return a + b


def test_add():
    ''' Test the add function to ensure pytest is working properly '''
    assert add(2, 3) == 5
