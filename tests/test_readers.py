import pweave

def test_markdown():
    """Test markdown reader"""
    pweave.weave("tests/readers/markdown_reader.pmd", doctype = "pandoc", informat = "markdown")
    assertSameContent("tests/readers/markdown_reader.md", "tests/readers/markdown_reader_ref.md")

def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())
