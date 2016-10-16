.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.44683.svg
   :target: http://dx.doi.org/10.5281/zenodo.44683
.. image:: https://travis-ci.org/mpastell/Pweave.svg?branch=master
   :target: https://travis-ci.org/mpastell/Pweave
.. image:: https://coveralls.io/repos/github/mpastell/Pweave/badge.svg?branch=master
   :target: https://coveralls.io/github/mpastell/Pweave?branch=master


Notas acerca de Pweave 0.3
---------------------
El branch maestro contiene el código para la futura versión 0.3, la cual rompe 
la compatibilidad con las últimas versiones lanzadas y sólo corre usando Python 3. El código tiene
muy buen code coverage y debería ser usable para quien quiera probarlo.

**Nuevas características notables.**

- El código corre usando jupyter_client dando la posibilidad de correr el código usando cualquier kernel instalado (incluyendo python 2) vía argumento `--kernel`. Algunas opciones de paquetes sólo trabajan en Python.
- Soporte para la magia de IPython y un rico rendimiento.
- Muchas pequeñas correcciones de salida y sintaxis sobresaliente incluyendo la renderización de los rastreos correctamente.
- Salida directamente a cuadernos Jupyter con chunk points preservadas como metadatos ->
con capacidad de usar plantillas nbconvert personalizadas además de la orden interna de formateadores.

Acerca de Pweave
-------------

Pweave es un generador de reportes científico y una herramienta de Programación Literaria
para Python. Pweave puede capturar los resultados y gráficas del análisis
de datos y trabaja muy bien con NumPy, SciPy and matplotlib. Es capaz de correr
código de Python a partir de la fuente del documento e incluye los resultados y captura
`matplotlib <http://matplotlib.sourceforge.net/>`_ gráficas en la salida.

Puede producir salidas reST, Sphinx, Latex, HTML y markdown (pandoc and leanpub)
a partir de múltiples formatos de entrada.

- Noweb usa `noweb <http://www.cs.tufts.edu/~nr/noweb/>`_ para separar código de la documentación.
- Markdown. Corre código de bloques de código markdown.
- Script. Python script margen especial en comentarios.

Pweave es bueno para crear reportes, tutoriales, presentaciones, etc. con código de python incrustado y puede ser usado para hacer sitios web juntos. ejemplos Sphinx or rest2web.

Características
---------

* Compatibilidad con Python 3.4 y 3.5
* **Ejecuta código de Python** en trozos y **captura** entrada y salida para un reporte.
* **Usa trozos de código** por ejemplo, el código es ejecutado, pero no mostrado en la salida.
* Captura gráficas matplotlib
* Evalúa código en línea en los trozos de documentación marcados usando ``<% %>`` y ``<%= %>``.
* Oculta todo el código y resultados de las ejecuciones previas para una generación de reportes
rápida cuando sólo estás trabajando en la documentación. Código en linea será ocultado en el modo de documentación.
* Soporta reST, LaTeX, HTML o markdown para trozos de documento.
Publica reporte de scripts Python. Similar a R markdown.
* Ejecuta líneas de código o intérprete.

Instalación
-----------------------

Desde PyPi::

  pip install --upgrade Pweave

con conda::

  conda install -c mpastell pweave

o descarga el código fuente y ejecútalo::

  python setup.py install

La documentación de Pweave puede encontrarse desde el sítio webhttp://mpastell.com/pweave

Notas de la versión
-------------

Ve `GHANGELOG.txt <https://github.com/mpastell/Pweave/blob/master/CHANGELOG.txt>`_ para cambios en cada versión.
Información de licencia.
-------------------

Ve el archivo "LICENSE" para información en el historial de este
software, términos & condiciones para su uso y una EXCLUSIÓN DE TODA
GARANTÍA.

