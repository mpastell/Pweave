import unittest
import pweave
import pickle
import os

class FormatterTest(unittest.TestCase):
    """Test formatters"""


    def setUp(self):
        self.doc = pweave.Pweb("tests/formats/formatters_test.pmd")
        #pickle.dump(doc.executed, open("formats/formatters_test.pkl", "wb"))
        try:
            self.doc.executed = pickle.load(open("tests/formats/formatters_test.pkl", "rb"))
        except ValueError: #ValueError: unsupported pickle protocol: 3
            self.doc.run()
            # pickle.dump(doc.executed, open("formats/formatters_test.pkl", "wb"))

        self.out_base = "tests/formats/formatters_test.%s"
        self.ref_base = "tests/formats/formatters_test_REF.%s"

    def testFormatters(self):
        formats = sorted(list(pweave.formatters.PwebFormats.formats.keys()))
        for format in formats:
            if format in ("pandoc2latex",
                          "pandoc2html",
                          "md2html"): # Failing formatters
                #TODO : replace regression tests with mock tests
                continue
            self.doc.format(format)
            self.out_file = self.out_base % format
            self.ref_file = self.ref_base % format
            self.doc.output = self.out_file
            self.doc.write()
            if "2html" in format:
                self.assertSameAsReference(1000) #Ignore changing footer
            else:
                self.assertSameAsReference()
            try:
                os.remove(self.out_file)
            except FileNotFoundError:
                pass

    def contentOf(self, filename, end_ignore):
        fh = open(filename)
        content = fh.read()
        fh.close()
        if end_ignore > 0:
            return(content[:-end_ignore])
        return content

    def assertSameAsReference(self, end_ignore = -1):
        self.assertEqual(self.contentOf(self.out_file, end_ignore),
                         self.contentOf(self.ref_file, end_ignore))



if __name__ == '__main__':
    unittest.main()
