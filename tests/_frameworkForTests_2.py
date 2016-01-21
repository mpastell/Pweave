__author__ = 'abukaj'
import unittest

from _frameworkForTests_common import ParametricTestsMetaclass

class ParametricTests(unittest.TestCase):
    __metaclass__ = ParametricTestsMetaclass