About Pweave
-------------

Pweave is a scientific report generator and a literate programming
tool for Python. Pweave can capture the results and plots from data
analysis and works well with numpy, scipy and matplotlib. Pweave is
inspired by `Sweave
<http://www.stat.uni-muenchen.de/~leisch/Sweave/>`_, an excellent tool
for R programmers, and the syntax is mostly compatible with it.

Pweave uses the noweb syntax for separating code from documentation,
but it also supports ERB style evaluation of inline code.  Pweave is
able to weave a python code between <<>>= and @ blocks and include the
results and capture matplotlib plots in the document. Additionally it
supports evaluating inline code in documentation chunks using <% %>
(code will be evaluated in place) and <%= %> (result of expression
will be printed) tags. It supports reST, Sphinx, Latex, and Pandoc
markdown markups. Pweave is good for creating reports and tutorials. It canalso be used to make websites together with Sphinx or rest2web.

Features:
----------

* **Execute python code** in the chunks and **capture** input and output to a report.
* **Use hidden code chunks,** i.e. code is executed, but not printed in the output file.
* Capture matplotlib graphics.
* Evaluate inline code in documentation chunks
* Cache all code and results from previous runs for superfast report
  generation when you are only working with documentation. Inline code
  will be hidden in documentation mode.
* Run from command line or interpreter

Install:
--------

With easy_install:::

  easy_install -U Pweave

Or download the source package and run:::

  python setup.py install

Documentation
-------------

Pweave documentation can be found from the website http://mpastell.com/pweave
