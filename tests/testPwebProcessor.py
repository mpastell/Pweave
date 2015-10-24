#!/usr/bin/env python
# encoding: utf-8
import unittest
import pweave

class LoadTermTest(unittest.TestCase):
    def setUp(self):
        self.processor = pweave.PwebProcessor('DummyParse',
                                              'DummySource',
                                              'DummyMode',
                                              'DummyFormatdict')
        
    def testOneLiner(self):
        self.checkOutput('print(123)\n',
                         '\n>>> print(123)\n123\n')

    def testNoEndingNL(self):
        self.checkOutput('print(123)',
                         '\n>>> print(123)\n123\n')

    def testTwoLines(self):
        self.checkOutput('a = 42\nprint(a)\n',
                         '\n>>> a = 42\n>>> print(a)\n42\n')

    def testNestedOneLineBody(self):
        self.checkOutput('for i in range(3):\n    print(i)\n',
                         '\n>>> for i in range(3):\n...     print(i)\n... \n0\n1\n2\n')

    def testNestedTwoLineBody(self):
        self.checkOutput('for i in range(3):\n    print(i)\n    print(i**2)\n',
                         '\n>>> for i in range(3):\n...     print(i)\n...     print(i**2)\n... \n0\n0\n1\n1\n2\n4\n')

    def testNestedTwoLineBodySeparatedWithWhiteSpaceLine(self):
      self.checkOutput('for i in range(3):\n    print(i)\n \n    print(i**2)\n',
                       '\n>>> for i in range(3):\n...     print(i)\n...  \n...     print(i**2)\n... \n0\n0\n1\n1\n2\n4\n')

    def testNestedOneLinerThenOneLiner(self):
        self.checkOutput('for i in range(3):\n    print(i)\n\nprint(1 + 2)\n',
                         '\n>>> for i in range(3):\n...     print(i)\n... \n0\n1\n2\n>>> print(1 + 2)\n3\n')

    def testNestedBlockValidBeforeDobleNestedBlockAppears(self):
      self.checkOutput('for i in range(2):\n    print(i)\n    if i > 0:\n        print("one")',
                       '\n>>> for i in range(2):\n...     print(i)\n...     if i > 0:\n...         print("one")\n... \n0\n1\none\n')

    def testRuntimeFailingCode(self):
      self.checkOutput('for i in range(3):\n    print(i)\n    if i == 1:\n        raise Exception("foo")\n\nprint(42)\n',
                       '\n>>> for i in range(3):\n...     print(i)\n...     if i == 1:\n...         raise Exception("foo")\n... \n0\n1\nTraceback (most recent call last):\n  File "DummySource", line 4, in <module>\nException: foo\n>>> print(42)\n42\n')

    def testSyntaxError(self):
      self.checkOutput('def f\nprint(42)\n',
                       '\n>>> def f\n  File "DummySource", line 1\n    def f\n        ^\nSyntaxError: invalid syntax\n>>> print(42)\n42\n')

    def testIndentationError(self):
      self.checkOutput('def f():\n    print(12)\n  print(8)\nprint(42)\n',
                       '\n>>> def f():\n...     print(12)\n...   print(8)\n  File "DummySource", line 3\n    print(8)\n           ^\nIndentationError: unindent does not match any outer indentation level\n>>> print(42)\n42\n')


    def checkOutput(self, inStr, outStr):
        self.assertEqual(outStr,
                         self.processor.loadterm(inStr))


if __name__ == '__main__':
    unittest.main()
