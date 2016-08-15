import pweave

def test_cache():
    """Test caching shell"""
    pweave.weave("tests/processors/processor_test.mdw", docmode = True, doctype = "markdown", informat = "markdown")
    pweave.weave("tests/processors/processor_test.mdw", docmode = True, doctype = "markdown", informat = "markdown")
    assertSameContent("tests/processors/processor_test.md", "tests/processors/processor_cache_ref.md")

def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())


if __name__ == '__main__':
    test_cache()
