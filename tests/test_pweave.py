import os
import errno

import pweave


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# make a figure dir if it doesn't exist
mkdir_p('tests/figures/tests')


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

    # Compare the outfile and the ref
    out = open(outfile)
    ref = open(REF)
    assert(out.read() == ref.read())

def test_continue_option():
    """Test documenting a class in multiple chunks using continue option"""
    REF = 'tests/ar_yw_ref.md'
    infile = 'tests/ar_yw.mdw'
    outfile = 'tests/ar_yw.md'
    pweave.weave(file=infile, doctype="pandoc")

    # Compare the outfile and the ref
    out = open(outfile)
    ref = open(REF)
    assert(out.read() == ref.read())



def test_nbformat():
    """Test whether we can write an IPython Notebook.
    """
    REF = 'tests/simple_REF.ipynb'
    infile = 'tests/simple.mdw'
    outfile = 'tests/simple.ipynb'
    # pandoc_args = None skips the call to pandoc
    pweave.convert(file=infile, informat="noweb", outformat="notebook")

    # Compare the outfile and the ref
    out = open(outfile)
    ref = open(REF)
    assert(out.read() == ref.read())
