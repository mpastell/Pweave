import os

import unittest

class ParametricTestsMetaclass(type):
    def __new__(mcl, name, bases, attrs):
        try:
            tests = attrs['_tests']
            testGenerator = attrs['_testGenerator']

        except KeyError:
            pass

        else:
            del attrs['_tests']
            del attrs['_testGenerator']

            for name, params in tests.items():

                args, kwargs = params
                methodName = 'test' + name
                attrs[methodName] = testGenerator(methodName, *args, **kwargs)

        return type.__new__(mcl, name, bases, attrs)

class ParametricTests(unittest.TestCase):
    __metaclass__ = ParametricTestsMetaclass

class RegressionTest(ParametricTests):
    TESTDIR = '.'

    def assertSameAsReference(self, reference=None):
        try:
            self.assertEqual(self.contentOf(reference if reference is not None else self.REFERENCE),
                             self.contentOf(self.OUTFILE))
        except AssertionError:
            raise AssertionError("{ref} and {out} differs\ntry:\n$ vimdiff {ref} {out}".format(
                                 ref=self.absPathTo(self.REFERENCE),
                                 out=self.absPathTo(self.OUTFILE)))

    def assertSameAsPattern(self, __pattern=None, **kwargs):
      try:
        self.assertEqual(self.contentOf(__pattern).format(**kwargs),
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
