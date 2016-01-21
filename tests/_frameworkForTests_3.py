import unittest

from _frameworkForTests_common import ParametricTestsMetaclass

class ParametricTests(unittest.TestCase, metaclass=ParametricTestsMetaclass):
    pass