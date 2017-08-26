
Pweave Basics
=============

.. index:: source document, output document

Pweave documents
________________

A Pweave input document contains documentation and code separated with special
markup. Pweave supports several input formats for different purposes. All of the
source formats produce identical output for code. You need to tell the input format
to Pweave using ``-i`` command line option.

Code chunk formats
------------------

markdown
++++++++

Pweave can run code from fenced markdown python code blocks. It is
recommended to ``.pmd`` file extension.

Sample code block syntax:

.. code-block:: md

  ```python
  x = np.linspace(0, 2*np.pi)
  plt.plot(x, np.sin(x))
  ```

Example document: :download:`FIR_designp.pmd <examples/FIR_designp.pmd>` and
output: :download:`FIR_designp.html <examples/FIR_designp.html>` compiled running:

.. code-block:: bash

  pweave -f md2html FIR_designp.pmd

All of the following are valid ways to define a code chunk:

::

  ```python
  ```{python}
  ```{.python}

You can define `chunk options <chunks.html>`__:

::

  ```{python, caption = "Some figure"}
  ```python, echo=False


noweb
+++++

Noweb syntax for defining code chunks has been adopted from  `Sweave
<http://www.stat.uni-muenchen.de/~leisch/Sweave/>`_.

Code chunk starts with a line marked with ``<<>>=`` or ``<<options>>=`` and end
with line marked with ``@``. The code between the start and end markers
is executed and the output is captured to the output document.

**Example:** A code chunk that saves and displays a 12 cm wide image
and hides the source code:

::

  <<fig = True, width = '12 cm', echo = False>>=
  from pylab import *
  plot(arange(10))
  show()
  @



Documentation chunk
-------------------

 The rest of the document is just copied to ouput and can be written with
 several different markup languages. See `formats <formats.html>`_ page for
 a list of supported output formats.

Inline code
-----------

 Pweave supports evaluating inline code in documentation chunks
 using ``<% %>`` (code will be evaluated in place) and ``<%= %>``
 (result of expression will be printed) tags. Inline code will not
 be included in weaved document.

.. versionadded:: 0.2

.. index:: options, figures, inline code chunks


Terminology
-----------

.. describe:: Source document

   Contains a mixture of documentation and code chunks. Pweave will
   evaluate the code and leave the documentation chunks as they
   are. The documentation chunks can be written either with reST,Latex
   or Pandoc markdown. The source document is processed using
   *Pweave*, which gives us the formatted output document.

.. describe:: Weaved document

   Is produced by Pweave from the source document. Contains the
   documentation, original code, the captured outputof the code and
   optionally captured `matplotlib
   <http://matplotlib.sourceforge.net/>`_ figures.

.. describe:: Source code

   Is produced by Pweave from the source document. Contains the source
   code extracted from the code chunks.

.. index::  syntax, code chunk, documentation chunk
