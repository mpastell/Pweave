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
            self.TESTDIR = os.path.join('weave', doctype)
            infile = self.absPathTo(filename + 'w')
            self.setNewOutfile(filename)

            pweave.weave(infile, doctype=doctype,
                output=self.absPathTo(filename),
                **kwargs)

            basename, _, ext = filename.rpartition('.')
            self.REFERENCE = self.absPathTo(basename + '_REF.' + ext)
            self.assertSameAsReference()

        testMethod.__name__ = name
        return testMethod

    _tests = {
              'Simple': (['pandoc', 'simple.md'], {}),
              'ClassInMultipleChunksUsingContinueOption': (['pandoc', 'ar_yw.md'], {}),
              'InlineCode': (['pandoc', 'inline_chunks.md'], {}),
              #'TerminalEmulation': (['tex', 'term_test.tex'], {}), Needs inspection
              'FIR_FilterExampleTex': (['tex', 'FIR_design_verb.tex'], {}),
              'WrapAndCodeOutput': (['texminted', 'wrap_test.tex'], {})
              }



class ConvertTest(RegressionTest):
    """Test pweave-convert
    """
    TESTDIR = 'convert'

    def _testGenerator(name, infile, informat, outformat, outext, python={2, 3}):
        def testMethod(self):
            basename, _, _ = infile.rpartition('.')
            outfile = basename + '.' + outext
            self.setNewOutfile(outfile)

            pweave.convert(self.absPathTo(infile),
                           informat=informat,
                           outformat=outformat)

            self.REFERENCE = self.absPathTo(basename + '_REF.' + outext)
            self.assertSameAsReference()

        testMethod.__name__ = name
        return testMethod

    _tests = {
              'Convert': (['convert_test.txt', 'script', 'noweb', 'Pnw'], {}),
              'Nbformat': (['simple.mdw', 'noweb', 'notebook', 'ipynb'], {}),
             }


if __name__ == '__main__':
    unittest.main()
