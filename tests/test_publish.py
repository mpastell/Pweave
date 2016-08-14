import pweave
import os, io

def test_publish():
    """Test pypublish"""
    pweave.publish("tests/publish/publish_test.txt", doc_format="html")
    test = io.open("tests/publish/publish_test.html", "r").read().encode("utf-8")
    ref = io.open("tests/publish/publish_test_ref.html", "r").read().encode("utf-8")
    #Leave out the changing footer
    assert (test[:len(test) - 400] == ref[:len(test) - 400])

def test_publish_cell():
    """Test pypublish cell format"""
    pweave.publish("tests/publish/publish_test_cell.txt", doc_format="html")
    test = io.open("tests/publish/publish_test_cell.html", "r").read().encode("utf-8")
    ref = io.open("tests/publish/publish_test_ref.html", "r").read().encode("utf-8")
    #Leave out the changing footer
    assert (test[:len(test) - 400] == ref[:len(test) - 400])


if __name__ == '__main__':
    test_publish()
    test_publish_cell()
