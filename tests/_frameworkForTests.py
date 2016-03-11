import os
import sys

if sys.version_info[0] < 3:
    try:
        from _frameworkForTests_2 import ParametricTests

    except ImportError:
        from ._frameworkForTests_2 import ParametricTests

else:
  try:
    from _frameworkForTests_3 import ParametricTests

  except ImportError:
    from ._frameworkForTests_3 import ParametricTests

class RegressionTest(ParametricTests):
    TESTDIR = '.'

    def assertSameAsReference(self):
        try:
            self.assertEqual(self.contentOf(self.REFERENCE),
                             self.contentOf(self.OUTFILE))
        except AssertionError:
            raise AssertionError("{ref} and {out} differs\ntry:\n$ vimdiff {ref} {out}".format(
                                 ref=self.absPathTo(self.REFERENCE),
                                 out=self.absPathTo(self.OUTFILE)))

    def absPathTo(self, filename):
        return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            self.TESTDIR,
                                            filename))

    def contentOf(self, filename):
        fh = open(self.absPathTo(filename))
        content = fh.read()
        fh.close()
        return content

    def removeFile(self, name):
        try:
            os.remove(self.absPathTo(name))

        except OSError:
            pass

    def setNewOutfile(self, name):
        self.removeFile(name)
        self.OUTFILE = name
