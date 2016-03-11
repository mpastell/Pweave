import unittest

try:
    from _frameworkForTests_common import ParametricTestsMetaclass

except ImportError:
    from ._frameworkForTests_common import ParametricTestsMetaclass

class ParametricTests(unittest.TestCase, metaclass=ParametricTestsMetaclass):
    pass