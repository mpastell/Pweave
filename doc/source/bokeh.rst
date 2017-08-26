
Using Bokeh with Pweave
=======================

.. index:: bokeh

Pweave can capture `Bokeh <http://bokeh.pydata.org>`__ plots with the help of
few utility functions.

.. autofunction:: pweave.bokeh.output_pweave

.. autofunction:: pweave.bokeh.show

Here is a simple example:

.. code-block:: md

  ```python
  from bokeh.plotting import figure
  from pweave.bokeh import output_pweave, show

  output_pweave()

  x = [1, 2, 3, 4, 5]
  y = [6, 7, 2, 4, 5]
  p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')
  p.line(x, y, legend="Temp.", line_width=2)

  show(p)
  ```
