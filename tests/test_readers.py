import pweave

def test_markdown():
    """Test markdown reader"""
    pweave.weave("tests/markdown_reader.mdw", doctype = "leanpub", informat = "markdown")
    assertSameContent("tests/markdown_reader.txt", "tests/markdown_reader_ref.md")

def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())
