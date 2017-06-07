"""Integration test pweave by comparing output to a known good
reference.

N.B. can't use anything in the .mdw that will give different
outputs each time. For example, setting term=True and then
calling figure() will output a matplotlib figure reference. This
has a memory pointer that changes every time.
"""

import unittest
import os
import pweave
try:
    from tests._frameworkForTests import RegressionTest
except:
    from _frameworkForTests import RegressionTest

class WeaveTest(RegressionTest):
    def _testGenerator(name, doctype, filename, kwargs={}, python={2, 3}):
        def testMethod(self):
            for _ in range(1000):
                self.TESTDIR = os.path.join('weave', doctype)
                infile = self.absPathTo(filename + 'w')
                self.setNewOutfile(filename)

                pweave.weave(infile, doctype=doctype, **kwargs)

                basename, _, ext = filename.rpartition('.')
                self.REFERENCE = self.absPathTo(basename + '_REF.' + ext)
                self.assertSameAsReference()

        testMethod.__name__ = name
        return testMethod

    _tests = {
              'TerminalEmulation': (['tex', 'nondeterministicFail.tex'], {}),
              }


if __name__ == '__main__':
    unittest.main()
