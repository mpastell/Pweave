import pweave

#Inline code is hidden for cached docs
def test_tex_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "tex", informat = "markdown")
    return(True)

def test_rst_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "rst", informat = "markdown")
    return(True)

def test_leanpub_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "leanpub", informat = "markdown")
    return(True)

def test_pandoc_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc", informat = "markdown")
    return(True)

def test_html_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "html", informat = "markdown")
    return(True)

def test_md2html_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "md2html", informat = "markdown")
    return(True)

def test_pandoc2html_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc2html", informat = "markdown")
    return(True)

def test_pandoc2latex_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "pandoc2latex", informat = "markdown")
    return(True)

def test_sphinx_format():
    """Test caching shell"""
    pweave.weave("tests/formats/formatters_test.pmd", doctype = "sphinx", informat = "markdown")
    return(True)
