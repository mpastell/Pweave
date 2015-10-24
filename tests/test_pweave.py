import pweave


def test_pandoc():
    """Integration test pweave by comparing output to a known good
    reference.

    N.B. can't use anything in the .mdw that will give different
    outputs each time. For example, setting term=True and then
    calling figure() will output a matplotlib figure reference. This
    has a memory pointer that changes every time.
    """
    REF = 'tests/simple_REF.md'
    infile = 'tests/simple.mdw'
    outfile = 'tests/simple.md'
    pweave.weave(file=infile, doctype="pandoc")

    assertSameContent(REF, outfile)


def test_continue_option():
    """Test documenting a class in multiple chunks using continue option"""
    REF = 'tests/ar_yw_ref.md'
    infile = 'tests/ar_yw.mdw'
    outfile = 'tests/ar_yw.md'
    pweave.weave(file=infile, doctype="pandoc")

    assertSameContent(REF, outfile)


def test_convert():
    """Test pweave-convert"""
    REF = 'tests/convert_test_ref.Pnw'
    infile = 'tests/convert_test.txt'
    outfile = 'tests/convert_test.Pnw'
    pweave.convert(infile, informat="script", outformat="noweb")
    assertSameContent(REF, outfile)


def test_nbformat():
    """Test whether we can write an IPython Notebook.
    """
    REF = 'tests/simple_REF.ipynb'
    infile = 'tests/simple.mdw'
    outfile = 'tests/simple.ipynb'
    # pandoc_args = None skips the call to pandoc
    pweave.convert(file=infile, informat="noweb", outformat="notebook")

    assertSameContent(REF, outfile)


def test_inline_chunks():
    """Test inline code"""
    REF = 'tests/inline_chunks_ref.md'
    infile = 'tests/inline_chunks.mdw'
    outfile = 'tests/inline_chunks.md'
    pweave.weave(file=infile, doctype="pandoc")

    assertSameContent(REF, outfile)


def test_octave():
    """Test running Octave code"""
    REF = 'tests/octave_test_ref.md'
    infile = 'tests/octave_test.mdw'
    outfile = 'tests/octave_test.md'
    pweave.weave(file=infile, doctype="pandoc", shell="octave")

    assertSameContent(REF, outfile)


def test_term():
    """Test Python terminal emulation

    Eval statements might not work with ipython properly (code compiled differently)"""
    REF = 'tests/term_test_ref.tex'
    infile = 'tests/term_test.texw'
    outfile = 'tests/term_test.tex'
    pweave.weave(file=infile, doctype="tex", shell="python")

    assertSameContent(REF, outfile)


def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert (out.read() == ref.read())

#Output contains date and version number, test needs to be fixed
# def test_publish():
#     """Test pweave.publish"""
#     REF = 'tests/publish_test_ref.html'
#     infile = 'tests/publish_test.txt'
#     outfile = 'tests/publish_test.html'
#     pweave.publish("tests/publish_test.txt")
#     assert(open(outfile).read() == open(REF).read())
