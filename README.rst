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

* Supports Python 2 and Python 3. Tested with 2.7 and 3.4. as of release 0.22.
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

Release Notes
-------------

**Release 0.22.1**

* Fixed a bug with inline code chunks.

**Release 0.22**

* Package global options moved to pweave.rcParams. This is a breaking
  change if you have used Pweb class to modify Pweave options. Should not affect commandline usage.
* Renamed pweave.pweave to pweave.weave, pweave.ptangle to pweave.tangle
* Python 3 compatibilty, Thanks to Grant Goodyear https://github.com/g2boojum
* Publishing of scripts from command line : pypublish script
* Conversion between input formats and markups: Pweave-convert script
  - Convert to IPython notebooks by Aaron O'Leary https://github.com/aaren
* Possibility to run shell code from Pweave. See `engine` chunk option.
* New input formats:
  - Script
  - IPython notebook
* Bugfix: setting figure format from command line fixed.
* Ipython terminal
* Source option for chunks
  - Read from module
  - Read from file
* Multichunk blocks: complete option
* rst format uses `.. codeblock::` python directive for code chunks.
* Output formats:
  - Leanpub markdown
* New options for figures
  - f_size ( (8,6) ) Saved figure size in inches a tuple (w, h) 
  - f_env (None) Environment that goes around figure e.g. sidefigure
  - f_spines (True) removes spines from figure right and top if False.
  - complete (False)
  - source: Read chunk source from file or python module or file
  - engine: Choose engine running the code. "python" or "shell"


Release notes for previous versions are in: http://mpastell.com/pweave/release.html 

License information
-------------------

See the file "LICENSE" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES.
