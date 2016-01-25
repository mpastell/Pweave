"""Integration test pweave by comparing output to a known good
reference.

N.B. can't use anything in the .mdw that will give different
outputs each time. For example, setting term=True and then
calling figure() will output a matplotlib figure reference. This
has a memory pointer that changes every time.
"""

import unittest
import sys

import pweave
from tests._frameworkForTests import RegressionTest


class PandocTest(RegressionTest):
    TESTDIR = 'pandoc'

    def _testGenerator(name, filename, python={2, 3}):
        def testMethod(self):
            infile = self.absPathTo(filename + '.mdw')
            self.setNewOutfile(filename + '.md')

            pweave.weave(infile,
                         doctype="pandoc")

            self.REFERENCE = self.absPathTo(filename + '_REF.md')
            self.assertSameAsReference()

        testMethod.__name__ = name
        version = sys.version_info[0]
        if version not in python:
            return unittest.skip('{test} skipped beacause of inappropriate Python version ({v})'.format(
                test = name,
                v = version))(testMethod)

        return testMethod

    _tests = {
              'Simple': (['simple'], {}),
              'ClassInMultipleChunksUsingContinueOption': (['ar_yw'], {}),
              'InlineCode': (['inline_chunks'], {}),
              }


class ConvertTest(RegressionTest):
    """Test pweave-convert
    """
    TESTDIR = 'convert'
    REFERENCE = 'convert_test_ref.Pnw'
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


class TermTest(RegressionTest):
    """Test Python terminal emulation

    Eval statements might not work with ipython properly (code compiled differently)"""
    TESTDIR = 'term'
    REFERENCE = 'term_test_ref.tex'
    INFILE = 'term_test.texw'
    OUTFILE = 'term_test.tex'

    def testTerm(self):
        pweave.weave(file=self.absPathTo(self.INFILE),
                     doctype="tex",
                     shell="python")
        self.assertSameAsReference()


class WrapTest(RegressionTest):
    """Test wrap and code output. Issues #18 and #21"""
    TESTDIR = 'wrap'
    REFERENCE = 'wrap_test_ref.tex'
    INFILE = 'wrap_test.texw'
    OUTFILE = 'wrap_test.tex'

    def testWrap(self):
        pweave.weave(file=self.absPathTo(self.INFILE),
                     doctype="texminted")
        self.assertSameAsReference()


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