import os
import unittest

__author__ = 'abukaj'


class RegressionTest(unittest.TestCase):
    TESTDIR = '.'

    def assertSameAsReference(self):
        try:
            self.assertEqual(self.contentOf(self.REFERENCE),
                             self.contentOf(self.OUTFILE))
        except AssertionError:
            raise AssertionError("{ref} and {out} differs".format(
                                 ref=self.absPathTo(self.REFERENCE),
                                 out=self.absPathTo(self.OUTFILE)))

    def absPathTo(self, filename):
        return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            self.TESTDIR,
                                            filename))

    def contentOf(self, filename):
        return open(self.absPathTo(filename)).read()

    def tearDown(self):
        os.remove(self.absPathTo(self.OUTFILE))
        pass