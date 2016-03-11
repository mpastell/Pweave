

.. code:: python

    from pylab import *
    x = linspace(0, 2*pi, 1000)
    




.. code:: python

    plot(x, sin(x))
    

.. image:: figures/formatters_test_figure2_1.png
   :width: 15 cm




.. figure:: figures/formatters_test_figure3_1.png
   :width: 15 cm

   Sinc function




.. code:: python

    plot(x, sinc(x))
    

.. figure:: figures/formatters_test_sinc_1.png
   :width: 15 cm

   Sinc function




.. code:: python

    plot(x, sinc(x))
    

.. figure:: figures/formatters_test_sinc_1.png
   :width: 50%

   Sinc function




.. code:: python

    plot(x, sinc(x))
    

.. figure:: figures/formatters_test_figure6_1.png
   :width: 50%

   Sinc function




.. code:: python

    plot(x, sinc(x))
    

.. figure:: figures/formatters_test_figure7_1.png
   :width: 50%

   Sinc function




.. code:: python

    for i in range(5):
      figure()
      plot(x, sinc(x*i))
    

.. figure:: figures/formatters_test_figure8_1.png
   :width: 50%

   Sinc function




.. code:: python

    for i in range(5):
      figure()
      plot(x, sinc(x*i))
    

.. image:: figures/formatters_test_figure9_1.png
   :width: 15 cm

.. image:: figures/formatters_test_figure9_2.png
   :width: 15 cm

.. image:: figures/formatters_test_figure9_3.png
   :width: 15 cm

.. image:: figures/formatters_test_figure9_4.png
   :width: 15 cm

.. image:: figures/formatters_test_figure9_5.png
   :width: 15 cm





.. code:: python

    print("Verbatim output")
    

.. code::

    Verbatim output
    
    




.. code:: python

    print("Hidden results!")
    



```


.. code::

    No echo!
    
    




No echo!




.. code:: python

    >>> for i in range(10):
    ...   print(i)
    ...
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    
    




.. code:: python

    print("pweave " * 20)
    

.. code::

    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    
    




.. code:: python

    print("pweave " * 20)
    

.. code::

    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave 
    




.. code:: python

    print("pweave " * 20)
    
    

.. code::

    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    
    




.. code:: python

    print("pweave " * 20)
    

.. code::

    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
    
    
    


