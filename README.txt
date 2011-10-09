About Pweave
-------------

Pweave is a scientific report generator and a literate programming
tool for Python. Pweave can capture the results and plots from data
analysis and works well with numpy, scipy and matplotlib. Pweave is
inspired by `Sweave
<http://www.stat.uni-muenchen.de/~leisch/Sweave/>`_, an excellent tool
for R programmers, and the syntax is mostly compatible with it.  Pweave
supports reST, Sphinx, Latex, and Pandoc markdown markups.

Pweave uses the noweb syntax for separating code from documentation,
but it also supports ERB style evaluation of inline code.  Pweave is
able to weave a python code between ``<<>>=`` and ``@`` blocks and
include the results and capture matplotlib plots in the
document. Inline code in documentation chunks is marked using ``<%
%>`` (code will be evaluated in place) and ``<%= %>`` (result of
expression will be printed) tags. Pweave is good for creating reports
and tutorials. It can also be used to make websites together with
Sphinx or rest2web.

Features:
----------

* **Execute python code** in the chunks and **capture** input and output to a report.
* **Use hidden code chunks,** i.e. code is executed, but not printed in the output file.
* Capture matplotlib graphics.
* Evaluate inline code in documentation chunks
* Cache all code and results from previous runs for fast report
  generation when you are only working with documentation. Inline code
  will be hidden in documentation mode.
* Supports reST, LaTeX or Pandoc markdown for document chunks
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
