import pweave
import os

#Inline code is hidden for cached docs
def test_cache():
    """Test caching shell"""
    pweave.weave("tests/processors/processor_test.mdw", docmode = True, doctype = "leanpub", informat = "markdown")
    pweave.weave("tests/processors/processor_test.mdw", docmode = True, doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processors/processor_test.txt", "tests/processors/processor_cache_ref.md")

def test_default_shell():
    """Test python shell"""
    pweave.weave("tests/processors/processor_test.mdw", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processors/processor_test.txt", "tests/processors/processor_default_ref.md")

def test_external_shell():
    """Test external python shell"""
    pweave.weave("tests/processors/processor_test.mdw", shell = "epython", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processors/processor_test.txt", "tests/processors/processor_external_ref.md")

def test_ipython_shell():
    """Test external python shell"""
    pweave.weave("tests/processors/ipy_processor_test.mdw", shell = "ipython", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processors/ipy_processor_test.txt", "tests/processors/ipy_processor_ref.md")


def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())
