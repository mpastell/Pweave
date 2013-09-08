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


def test_pweave():
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
    pweave.pweave(file=infile, doctype="pandoc", figdir='tests/figures')

    # Compare the outfile and the ref
    out = open(outfile)
    ref = open(REF)
    assert(out.read() == ref.read())
