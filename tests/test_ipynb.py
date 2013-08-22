import pweave


def test_nbformat():
    """Test whether we can write an IPython Notebook.
    """
    infile = 'tests/simple.mdw'
    # pandoc_args = None skips the call to pandoc
    pweave.convert(file=infile, informat="noweb", outformat="notebook")
