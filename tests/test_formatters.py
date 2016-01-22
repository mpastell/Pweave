import pweave
import unittest

try:
    from _frameworkForTests import RegressionTest

except ImportError:
    from ._frameworkForTests import RegressionTest

class WeaveFormatsTest(RegressionTest):
    TESTDIR = 'formats'
    INFILE = 'formatters_test.pmd'

    def _testGenerator(name, doctype, ext, reference):
        def testMethod(self):
            infile = self.absPathTo(self.INFILE)
            pweave.weave(infile,
                         doctype=doctype,
                         informat='markdown')
            self.OUTFILE = infile[:-3] + ext
            self.REFERENCE = self.absPathTo(reference)
            self.assertSameAsReference()

        testMethod.__name__ = name
        return testMethod

    _tests = {'Tex': (['tex', 'tex', 'formatters_test_REF.tex'], {}),
              'RST': (['rst', 'rst', 'formatters_test_REF.rst'], {}),
              'Leanpub': (['leanpub', 'txt', 'formatters_test_REF.txt'], {}),
              'Pandoc': (['pandoc', 'md', 'formatters_test_REF.md'], {}),
              'HTML': (['html', 'html', 'formatters_test_REF.html'], {}),
              }


#Inline code is hidden for cached docs
# def test_leanpub_format():
#     """Test caching shell"""
#     pweave.weave("tests/formats/formatters_test.pmd", doctype = "leanpub", informat = "markdown")
#     return(True)
# def test_pandoc_format():
#     """Test caching shell"""
#     pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc", informat = "markdown")
#     return(True)
# def test_html_format():
#     """Test caching shell"""
#     pweave.weave("tests/formats/formatters_test.pmd", doctype = "html", informat = "markdown")
#     return(True)

def test_md2html_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "md2html", informat = "markdown")
    return(True)

def test_pandoc2html_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc2html", informat = "markdown")
    return(True)

def test_pandoc2latex_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc2latex", informat = "markdown")
    return(True)

def test_sphinx_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "sphinx", informat = "markdown")
    return(True)


if __name__ == '__main__':
    unittest.main()