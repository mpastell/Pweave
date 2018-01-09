.. _publish:

Publishing scripts
==================

.. note:: You'll need Pweave >= 0.24 for this.

As option to using the noweb format Pweave can also publish html and pdf
documents from Python scripts with a specific format.

These scripts can be executed normally using Python or published to HTML with Pweave.
Documentation is written in markdown in lines starting with ``#'``, ``#%%`` or ``# %%`` ,
and code is executed and results are included in the published document.
``#%%`` is also  `code cell <https://pythonhosted.org/spyder/editor.html#how-to-define-a-code-cell>`_ mark up used in Spyder IDE.

The concept is similar to publishing documents with MATLAB or
using Knitr's `spin <http://yihui.name/knitr/demo/stitch/>`_.
Pweave will remove the first empty space from each line of documentation.


All lines that are not documentation are treated as code. You can set chunk options
using lines starting with ``#+``, ``#%%`` or ``# %%`` just before code
e.g. ``#+ term=True, caption='Fancy plots.'``. See the example below for the markup.


The scripts can be published using the `pypublish` scipts:

:download:`FIR_design.py <examples/FIR_design.py>`, :download:`FIR_design.html <examples/FIR_design.html>` , :download:`FIR_design.pdf <examples/FIR_design.pdf>` .

.. code:: shell

    pypublish FIR_design.py
    pypublish -f pdf FIR_design.py

You can use diffent themes with pypublish using ``-t`` command line option. The
default option is `skeleton <http://getskeleton.com>`_ , other options are
``pweave`` (the old theme), `bootstrap <http://getbootstrap.com>`_ , `cerulean <https://bootswatch.com/cerulean/>`_ and `journal <https://bootswatch.com/journal/>`_.

.. versionadded:: 0.25

Other mark ups with scripts
---------------------------

You can also use any pweave supported format in the comments and run pweave
using script as input. e.g to get latex output you can use:

.. code:: shell

    pweave -f tex FIR_design.py
