Code Chunk Options
__________________

Pweave currently has the following options for processing the code
chunks.

.. envvar:: name, label

   If the first option of chunk is unnamed it will become the chunk
   name, you can also set the chunk name using the name or label (*for
   Sweave compatibility*) keys. All of these definitions are equal
   ``<<analysis, Fig = True>>=``,  ``<<Fig = True, name =
   'analysis'>>=``,  ``<<Fig = True, label = 'analysis'>>=``. Chunk
   names are used for figure names, but expanding named chunks in the
   Pweave todo list.

.. versionadded:: 0.2

.. envvar:: echo = True or (False)

   Echo the python code in the output document. If False the source
   code will be hidden.

.. envvar:: evaluate = True or (False).

   Evaluate the code chunk. If False the chunk won't be executed.

.. envvar:: results = 'verbatim'

   The output format of the printed results. 'verbatim' for literal
   block, 'hidden' for hidden results or anything other string for raw
   output (I tend to use 'tex' for Latex and 'rst' for rest. Raw output
   is useful if you wan't to e.g. create tables from code chunks.


.. versionadded:: 0.12

.. envvar:: term = False or (True)

   If True the output emulates a terminal session i.e. the code chunk
   and the output will be printed as a `doctest block
   <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#doctest-blocks>`_. Can
   also be used in latex documents, where the output will formatted as
   verbatim.

.. envvar:: include = True or (False)

   If include is True generated figures are automatically included in
   the document otherwise figures are generated, but not
   included. This is useful if you want more control over figure
   formatting e.g. use subfigures in Latex.

.. versionadded:: 0.21

.. envvar:: fig = True or (False)

   Whether a matplotlib plot produced by the code chunk should be
   included in the file. The figure will be added with '.. image::'
   directive in .rst and \\includegraphics tag in .tex documents. See
   the 'caption' option if you want to use figure environment. As of
   version 0.21 Pweave supports multiple figures per code chunk.

.. envvar:: caption = ''

      A string providing a caption for the figure produced in the code
      chunk. Can only be used with 'fig = True' option.

.. envvar:: width

   The width of the created figure in the document (using format specific
   markup e.g. "12cm", "600px", "\linewidth"). The default width depends on the output format.

.. envvar:: f_size = (8,6)

  Saved matplotlib figure size in inches a tuple (w, h).

.. versionadded:: 0.22

.. envvar:: f_spines = True

  Removes spines from matplotlib figures right and top if False.

.. versionadded:: 0.22

.. envvar:: f_env

  Add environment that goes around figures in LaTex output e.g. sidefigure

.. versionadded:: 0.22

.. envvar:: f_pos = "htpb"

   Sets the figure position for latex figures.

.. versionadded:: 0.21

.. envvar:: wrap = True or (False,"code", "results")

   Controls wrapping of long lines. If True both code and output are
   wrapped to 75 characters. You can also specify "code" or "results" options to
   wrap only input or output.

.. versionadded:: 0.21

.. envvar:: complete = True

  Used to include code spanning multiple chunks before it get executed. Useful for e.g. documenting class definitions. Use complete = False all but the last chunk and set the last one as complete = True. Pweave executes all of the chunks together and includes the results after the last one. See:  :ref:`multi-chunk-example` example.

.. versionadded:: 0.22

.. envvar:: source

    Read chunk contents from file or python module or file. e.g. source = "mychunk.py".

.. versionadded:: 0.22
