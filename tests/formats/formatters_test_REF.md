

~~~~{.python}
from pylab import *
x = linspace(0, 2*pi, 1000)
~~~~~~~~~~~~~




~~~~{.python}
plot(x, sin(x))
~~~~~~~~~~~~~

![](figures/formatters_test_figure2_1.png)\



![Sinc function](figures/formatters_test_figure3_1.png)



~~~~{.python}
plot(x, sinc(x))
~~~~~~~~~~~~~

![Sinc function](figures/formatters_test_sinc_1.png)



~~~~{.python}
plot(x, sinc(x))
~~~~~~~~~~~~~

![Sinc function](figures/formatters_test_sinc_1.png)



~~~~{.python}
plot(x, sinc(x))
~~~~~~~~~~~~~

![Sinc function](figures/formatters_test_figure6_1.png)



~~~~{.python}
plot(x, sinc(x))
~~~~~~~~~~~~~

![Sinc function](figures/formatters_test_figure7_1.png)



~~~~{.python}
for i in range(5):
  figure()
  plot(x, sinc(x*i))
~~~~~~~~~~~~~

![Sinc function](figures/formatters_test_figure8_1.png)



~~~~{.python}
for i in range(5):
  figure()
  plot(x, sinc(x*i))
~~~~~~~~~~~~~

![](figures/formatters_test_figure9_1.png)\
![](figures/formatters_test_figure9_1.png)\
![](figures/formatters_test_figure9_1.png)\
![](figures/formatters_test_figure9_1.png)\
![](figures/formatters_test_figure9_1.png)\




~~~~{.python}
print("Verbatim output")
~~~~~~~~~~~~~

~~~~{.python}
Verbatim output

~~~~~~~~~~~~~




~~~~{.python}
print("Hidden results!")
~~~~~~~~~~~~~



```


~~~~{.python}
No echo!

~~~~~~~~~~~~~




No echo!




~~~~{.python}
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

~~~~~~~~~~~~~




~~~~{.python}
print("pweave " * 20)
~~~~~~~~~~~~~

~~~~{.python}
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave

~~~~~~~~~~~~~




~~~~{.python}
print("pweave " * 20)
~~~~~~~~~~~~~

~~~~{.python}
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave 
~~~~~~~~~~~~~




~~~~{.python}
print("pweave " * 20)

~~~~~~~~~~~~~

~~~~{.python}
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave

~~~~~~~~~~~~~




~~~~{.python}
print("pweave " * 20)
~~~~~~~~~~~~~

~~~~{.python}
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave
pweave pweave pweave pweave pweave pweave pweave pweave pweave pweave


~~~~~~~~~~~~~


