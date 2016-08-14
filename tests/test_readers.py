import pweave

def test_markdown():
    """Test markdown reader"""
    pweave.weave("tests/readers/markdown_reader.pmd", doctype = "pandoc", informat = "markdown")
    assertSameContent("tests/readers/markdown_reader.md", "tests/readers/markdown_reader_ref.md")

def test_script():
    """Test markdown reader"""
    doc = pweave.Pweb("tests/publish/publish_test.txt", informat="script")
    doc.tangle()
    assertSameContent("tests/publish/publish_test.py",
                      "tests/publish/publish_test_REF.py")



def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())

if __name__ == '__main__':
    test_markdown()
    test_script()
