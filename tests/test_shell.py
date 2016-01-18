import pweave
import os

#Inline code is hidden for cached docs
def test_cache():
    """Test caching shell"""
    pweave.weave("tests/processor_test.mdw", docmode = True, doctype = "leanpub", informat = "markdown")
    pweave.weave("tests/processor_test.mdw", docmode = True, doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processor_test.txt", "tests/processor_cache_ref.md")

def test_default_shell():
    """Test python shell"""
    pweave.weave("tests/processor_test.mdw", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processor_test.txt", "tests/processor_default_ref.md")

def test_external_shell():
    """Test external python shell"""
    pweave.weave("tests/processor_test.mdw", shell = "epython", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processor_test.txt", "tests/processor_external_ref.md")

def test_ipython_shell():
    """Test external python shell"""
    pweave.weave("tests/ipy_processor_test.mdw", shell = "ipython", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/ipy_processor_test.txt", "tests/ipy_processor_ref.md")


def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())
