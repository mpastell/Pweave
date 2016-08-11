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

            pweave.weave(infile, doctype=doctype, **kwargs)

            basename, _, ext = filename.rpartition('.')
            self.REFERENCE = self.absPathTo(basename + '_REF.' + ext)
            self.assertSameAsReference()

        testMethod.__name__ = name
        return testMethod

    _tests = {
              'Simple': (['pandoc', 'simple.md'], {}),
              'ClassInMultipleChunksUsingContinueOption': (['pandoc', 'ar_yw.md'], {}),
              'InlineCode': (['pandoc', 'inline_chunks.md'], {}),

              'TerminalEmulation': (['tex', 'term_test.tex'], {}),

              'FIR_FilterExampleTex': (['tex', 'FIR_design_verb.tex'], {})
              # TODO decide how to handle wrapping
              #'WrapAndCodeOutput': (['texminted', 'wrap_test.tex'], {})
              }


# class GivenTexDocumentWithPythonCodeGeneratingFigure(RegressionTest):
#     TESTDIR = 'weave/tex/'
#     INFILE = 'FIR_design_verb.texw'
#     FIGURES = [(2, 1), (2, 2), (3, 1), (4, 1)]
#     FIGURE_PATTERN = 'FIR_design_verb_figure{chunk}_{n}.pdf'
#
#     def testWhenOutputInDifferentDirectoryFiguresDirectoryIsWritenThere(self):
#         filename = 'FIR_design_verb/FIR_design.tex'
#         self.removeFigures('FIR_design_verb/figures')
#
#         self.setNewOutfile(filename)
#
#         pweave.weave(self.absPathTo(self.INFILE),
#                      output=self.absPathTo(filename),
#                      doctype='tex')
#
#         self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
#                                  figdir='figures')
#         self.checkFiguresExist('FIR_design_verb/figures')
#
#     def testWhenFigdirGivenFiguresAreWritenThere(self):
#       filename = 'FIR_design_verb/FIR_design_figdir.tex'
#       self.removeFigures('FIR_design_verb/figs')
#       self.setNewOutfile(filename)
#
#       pweave.weave(self.absPathTo(self.INFILE),
#                    output=self.absPathTo(filename),
#                    figdir='figs',
#                    doctype='tex')
#
#       self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
#                                figdir='figs')
#       self.checkFiguresExist('FIR_design_verb/figs')
#
#     def testWhenAbsoluteFigdirGivenFiguresAreWritenThere(self):
#       filename = 'FIR_design_verb/FIR_design_AbsoluteFigdir.tex'
#       relativeFigDir = 'absFigs'
#       figdir = self.absPathTo(relativeFigDir)
#       self.removeFigures(relativeFigDir)
#
#       self.setNewOutfile(filename)
#
#       pweave.weave(self.absPathTo(self.INFILE),
#                    output=self.absPathTo(filename),
#                    figdir=figdir,
#                    doctype='tex')
#
#       self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
#                                figdir=figdir)
#
#       self.checkFiguresExist(relativeFigDir)
#
#     def removeFigures(self, relativeFigDir):
#       for figure in self.__getFigures(relativeFigDir):
#         self.removeFile(figure)
#
#     def checkFiguresExist(self, relativeFigDir):
#       for figure in self.__getFigures(relativeFigDir):
#         self.assertTrue(os.path.exists(self.absPathTo(figure)))
#
#     def __getFigures(self, figdir='figures'):
#       for chunk, n in self.FIGURES:
#         yield os.path.join(figdir,
#                            self.FIGURE_PATTERN.format(chunk=chunk,
#                                                       n=n))
#
#
# class ConvertTest(RegressionTest):
#     """Test pweave-convert
#     """
#     TESTDIR = 'convert'
#
#     def _testGenerator(name, infile, informat, outformat, outext, python={2, 3}):
#         def testMethod(self):
#             basename, _, _ = infile.rpartition('.')
#             outfile = basename + '.' + outext
#             self.setNewOutfile(outfile)
#
#             pweave.convert(self.absPathTo(infile),
#                            informat=informat,
#                            outformat=outformat)
#
#             self.REFERENCE = self.absPathTo(basename + '_REF.' + outext)
#             self.assertSameAsReference()
#
#         testMethod.__name__ = name
#         version = sys.version_info[0]
#         if version not in python:
#             return unittest.skip('{test} skipped beacause of inappropriate Python version ({v})'.format(
#                 test = name,
#                 v = version))(testMethod)
#
#         return testMethod
#
#     _tests = {
#               'Convert': (['convert_test.txt', 'script', 'noweb', 'Pnw'], {}),
#               'Nbformat': (['simple.mdw', 'noweb', 'notebook', 'ipynb'], {}),
#              }



if __name__ == '__main__':
    unittest.main()
