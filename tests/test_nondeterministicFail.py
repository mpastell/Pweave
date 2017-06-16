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

class ReproducibleTest(RegressionTest):
    REPEAT = 100
    def _testGenerator(name, doctype, filename, kwargs={}, python={2, 3}):
        def testMethod(self):
            for i in range(self.REPEAT):
                print('START: run {}/{}'.format(i, self.REPEAT))

                self.TESTDIR = os.path.join('weave', doctype)
                infile = self.absPathTo(filename + 'w')
                self.setNewOutfile(filename)

                pweave.weave(infile, doctype=doctype, **kwargs)

                basename, _, ext = filename.rpartition('.')
                self.REFERENCE = self.absPathTo(basename + '_REF.' + ext)
                try:
                    self.assertSameAsReference()
                except AssertionError:
                    for row in pweave.DEBUG:
                        print(repr(row))
                    raise
                print('END: run {}/{}'.format(i, self.REPEAT))

        testMethod.__name__ = name
        return testMethod

    _tests = {
              'TerminalEmulation': (['tex', 'nondeterministicFail.tex'], {}),
              }


if __name__ == '__main__':
    unittest.main()
