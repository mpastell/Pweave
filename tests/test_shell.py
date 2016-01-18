import pweave
import os, io

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
    """Test ipython python shell"""
    pweave.weave("tests/processors/ipy_processor_test.mdw", shell = "ipython", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/processors/ipy_processor_test.txt", "tests/processors/ipy_processor_ref.md")


def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())

def test_publish():
    """Test pypublish"""
    pweave.publish("tests/publish/publish_test.txt", doc_format="html")
    test = io.open("tests/publish/publish_test.html", "r").read().encode("utf-8")
    ref = io.open("tests/publish/publish_test_ref.html", "r").read().encode("utf-8")
    #Leave out the changing footer
    assert (test[len(test) - 500] == ref[len(test) - 500])
