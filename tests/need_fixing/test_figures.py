import unittest
import sys
import os
import pweave
try:
    from tests._frameworkForTests import RegressionTest
except:
    from _frameworkForTests import RegressionTest


class GivenTexDocumentWithPythonCodeGeneratingFigure(RegressionTest):
    TESTDIR = 'weave/tex/'
    INFILE = 'FIR_design_verb.texw'
    FIGURES = [(2, 1), (2, 2), (3, 1), (4, 1)]
    FIGURE_PATTERN = 'FIR_design_verb_figure{chunk}_{n}.pdf'

    def testWhenOutputInDifferentDirectoryFiguresDirectoryIsWritenThere(self):
        filename = 'FIR_design_verb/FIR_design.tex'
        self.removeFigures('FIR_design_verb/figures')

        self.setNewOutfile(filename)

        pweave.weave(self.absPathTo(self.INFILE),
                     output=self.absPathTo(filename),
                     doctype='tex')

        self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
                                 figdir='figures')
        self.checkFiguresExist('FIR_design_verb/figures')

    def testWhenFigdirGivenFiguresAreWritenThere(self):
      filename = 'FIR_design_verb/FIR_design_figdir.tex'
      self.removeFigures('FIR_design_verb/figs')
      self.setNewOutfile(filename)

      pweave.weave(self.absPathTo(self.INFILE),
                   output=self.absPathTo(filename),
                   figdir='figs',
                   doctype='tex')

      self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
                               figdir='figs')
      self.checkFiguresExist('FIR_design_verb/figs')

    def testWhenAbsoluteFigdirGivenFiguresAreWritenThere(self):
      filename = 'FIR_design_verb/FIR_design_AbsoluteFigdir.tex'
      relativeFigDir = 'absFigs'
      figdir = self.absPathTo(relativeFigDir)
      self.removeFigures(relativeFigDir)

      self.setNewOutfile(filename)

      pweave.weave(self.absPathTo(self.INFILE),
                   output=self.absPathTo(filename),
                   figdir=figdir,
                   doctype='tex')

      self.assertSameAsPattern('FIR_design_verb/REF_tex.pattern',
                               figdir=figdir)

      self.checkFiguresExist(relativeFigDir)

    def removeFigures(self, relativeFigDir):
      for figure in self.__getFigures(relativeFigDir):
        self.removeFile(figure)

    def checkFiguresExist(self, relativeFigDir):
      for figure in self.__getFigures(relativeFigDir):
        self.assertTrue(os.path.exists(self.absPathTo(figure)))

    def __getFigures(self, figdir='figures'):
      for chunk, n in self.FIGURES:
        yield os.path.join(figdir,
                           self.FIGURE_PATTERN.format(chunk=chunk,
                                                      n=n))

    def assertSameAsPattern(self, __pattern=None, **kwargs):
        try:
            self.assertEqual(self.contentOf(__pattern).format(**kwargs),
                             self.contentOf(self.OUTFILE))
        except AssertionError:
            raise AssertionError("{ref} and {out} differs\ntry:\n$ vimdiff {ref} {out}".format(
                ref="",
                out=self.absPathTo(self.OUTFILE)))


if __name__ == '__main__':
    unittest.main()
