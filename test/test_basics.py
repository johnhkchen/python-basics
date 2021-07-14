import unittest


class TestBasicTraits(unittest.TestCase):
    def test_discoverable(self):
        self.assertNotEqual(0, 1)
