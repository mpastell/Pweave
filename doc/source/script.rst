
Using Pweave from Command Line
==============================

Weaving Pweave documents
________________________

Weaving a Pweave source file produces a document
that contains text and the weaved code together with its
evaluated output.  All of the produced figures are placed in the
'figures/' folder as a default.

**Pweave documents are weaved from the shell with the command:**

.. describe:: pweave [options] sourcefile

  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -f DOCTYPE, --format=DOCTYPE
                          The output format. Available formats:  tex, texminted,
                          texpweave, texpygments, rst, pandoc, markdown,
                          leanpub, sphinx, html, md2html, softcover,
                          pandoc2latex, pandoc2html, notebook Use Pweave -l to
                          list descriptions or see
                          http://mpastell.com/pweave/formats.html
    -i INFORMAT, --input-format=INFORMAT
                          Input format: noweb, markdown, notebook or script
    -k KERNEL, --kernel=KERNEL
                          Jupyter kernel used to run code: default is python3
    -o OUTPUT, --output=OUTPUT
                          Name of the output file
    -l, --list-formats    List output formats
    -m, --matplotlib      Disable matplotlib
    -d, --documentation-mode
                          Use documentation mode, chunk code and results will be
                          loaded from cache and inline code will be hidden
    -c, --cache-results   Cache results to disk for documentation mode
    -F FIGDIR, --figure-directory=FIGDIR
                          Directory path for matplolib graphics: Default
                          'figures'
    --cache-directory=CACHEDIR
                          Directory path for cached results used in
                          documentation mode: Default 'cache'
    -g FIGFORMAT, --figure-format=FIGFORMAT
                          Figure format for matplotlib graphics: Defaults to
                          'png' for rst and Sphinx html documents and 'pdf' for
                          tex
    -t MIMETYPE, --mimetype=MIMETYPE
                          Source document's text mimetype. This is used to set
                          cell type in Jupyter notebooks


Weave a markdown document. Output format is detected based on extension,
but in can be changed using the ```-f`` option:

::

  $ pweave FIR_design.pmd


Get options:

::

  $ pweave --help


Caching results
_______________

Pweave has documentation mode (invoked with ``-d``) that caches code
and all results from code chunks so you don't need to rerun the code
when you are only working on documentation. You can cache the results
using the `-c` option, if there are no cached results then
documentation mode will create the cache on first run.  Inline code
chunks will be hidden in documentation mode. Additionally Pweave will
warn you if the code in cached chunks has changed after the last run.

Tangling Pweave Documents
_________________________

Tangling refers to extracting the source code from Pweave
document. This can be done using Ptangle script::

  $ ptangle file

  $ ptangle ma.pnw
  Tangled code from ma.pnw to ma.py
