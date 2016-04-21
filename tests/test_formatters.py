import pweave
import unittest
import sys
import os

try:
    from _frameworkForTests import RegressionTest

except ImportError:
    from ._frameworkForTests import RegressionTest

class WeaveFormatsTest(RegressionTest):
    TESTDIR = 'formats'
    INFILE = 'formatters_test.pmd'

    def _testGenerator(name, doctype, ext, reference, python={2, 3}):
        def testMethod(self):
            infile = self.absPathTo(self.INFILE)
            self.setNewOutfile(infile[:-3] + ext)
            print("")
            pweave.weave(infile,
                         doctype=doctype,
                         informat='markdown')

            self.REFERENCE = self.absPathTo(reference)
            self.assertSameAsReference

        testMethod.__name__ = name
        version = sys.version_info[0]
        if version not in python:
            return unittest.skip('{test} skipped beacause of inappropriate Python version ({v})'.format(
              test = name,
              v = version))(testMethod)

        return testMethod

    _tests = {
              'TeX': (['tex', 'tex', 'formatters_test_REF.tex'], {}),
              'RST': (['rst', 'rst', 'formatters_test_REF.rst'], {}),
              'Leanpub': (['leanpub', 'txt', 'formatters_test_REF.txt'], {}),
              'Pandoc': (['pandoc', 'md', 'formatters_test_REF.md'], {}),
              'HTML': (['html', 'html', 'formatters_test_REF.html'], {}),
              # contains date
              # 'MdToHTML': (['md2html', 'html', 'formatters_test_md_REF.html'], {}),
              # 'PandocToHTML': (['pandoc2html', 'html', 'formatters_test_pandoc_REF.html'], {}),
              'PandocToLaTeX': (['pandoc2latex', 'tex', 'formatters_test_pandoc_REF.tex'],
                                {'python': {2}}),# output differs substantially depending on Python version
              'Sphinx': (['sphinx', 'rst', 'formatters_test_sphinx_REF.rst'], {}),
              }

if __name__ == '__main__':
    unittest.main()
