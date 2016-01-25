"""Integration test pweave by comparing output to a known good
reference.

N.B. can't use anything in the .mdw that will give different
outputs each time. For example, setting term=True and then
calling figure() will output a matplotlib figure reference. This
has a memory pointer that changes every time.
"""

import unittest
import sys
import os

import pweave
from tests._frameworkForTests import RegressionTest


class PandocTest(RegressionTest):
    def _testGenerator(name, doctype, filename, kwargs={}, python={2, 3}):
        def testMethod(self):
            self.TESTDIR = os.path.join('weave', doctype)
            infile = self.absPathTo(filename + 'w')
            self.setNewOutfile(filename)

            pweave.weave(infile, doctype=doctype, **kwargs)

            basename, _, ext = filename.rpartition('.')
            self.REFERENCE = self.absPathTo(basename + '_REF.' + ext)
            self.assertSameAsReference()

        testMethod.__name__ = name
        version = sys.version_info[0]
        if version not in python:
            return unittest.skip('{test} skipped beacause of inappropriate Python version ({v})'.format(
                test = name,
                v = version))(testMethod)

        return testMethod

    _tests = {
              'Simple': (['pandoc', 'simple.md'], {}),
              'ClassInMultipleChunksUsingContinueOption': (['pandoc', 'ar_yw.md'], {}),
              'InlineCode': (['pandoc', 'inline_chunks.md'], {}),
              'TerminalEmulation': (['tex', 'term_test.tex'], {'kwargs': {'shell': 'python'}}),
              'WrapAndCodeOutput': (['texminted', 'wrap_test.tex'], {}),
              }


class ConvertTest(RegressionTest):
    """Test pweave-convert
    """
    TESTDIR = 'convert'
    REFERENCE = 'convert_test_REF.Pnw'
    INFILE = 'convert_test.txt'
    OUTFILE = 'convert_test.Pnw'
    INFORMAT = 'script'
    OUTFORMAT = 'noweb'

    def testConvert(self):
        pweave.convert(self.absPathTo(self.INFILE),
                       informat=self.INFORMAT,
                       outformat=self.OUTFORMAT)
        self.assertSameAsReference()


class NbformatTest(ConvertTest):
    """Test whether we can write an IPython Notebook.
    """
    REFERENCE = 'simple_REF.ipynb'
    INFILE = 'simple.mdw'
    OUTFILE = 'simple.ipynb'
    INFORMAT = 'noweb'
    OUTFORMAT = 'notebook'



#def test_octave():
#    """Test running Octave code"""
#    REF = 'tests/octave_test_ref.md'
#    infile = 'tests/octave_test.mdw'
#    outfile = 'tests/octave_test.md'
#    pweave.weave(file=infile, doctype="pandoc", shell="octave")
#    assertSameContent(REF, outfile)


#Output contains date and version number, test needs to be fixed
# def test_publish():
#     """Test pweave.publish"""
#     REF = 'tests/publish_test_ref.html'
#     infile = 'tests/publish_test.txt'
#     outfile = 'tests/publish_test.html'
#     pweave.publish("tests/publish_test.txt")
#     assert(open(outfile).read() == open(REF).read())

if __name__ == '__main__':
    unittest.main()