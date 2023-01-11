import shutil

import pweave


def test_cache():
    """Test caching shell"""
    shutil.rmtree("tests/processors/cache", ignore_errors=True)
    pweave.weave("tests/processors/processor_test.pmd", docmode=True)
    pweave.weave("tests/processors/processor_test.pmd", docmode=True)
    assertSameContent(
        "tests/processors/processor_test.md", "tests/processors/processor_cache_ref.md"
    )


def assertSameContent(REF, outfile):
    out = open(outfile)
    ref = open(REF)
    assert out.read() == ref.read()


if __name__ == "__main__":
    test_cache()
