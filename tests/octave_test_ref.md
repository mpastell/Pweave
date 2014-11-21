# Using Octave with Pweave

You can also use Pweave to publish reports using GNU Octave. The
feature is implemented in development branch in will be most likely
released with Pweave 0.23.

**Features:**
* Inline code and noweb style chunks
* Capturing of figures

**Limitations**
* Output formatting is currently only implemented for pandoc
* No terminal chunks
* Only one figure/chunk

Install Pweave from Github  and try it out using:

    pweave -s octave -f pandoc octave_sample.mdw


You can use inline code chunks like in Python documents: 

Give y value 300  in hidden chunk. 

And let's verify that it worked:


~~~~{.python}
y
~~~~~~~~~~~~~

~~~~{.python}
y =  300

~~~~~~~~~~~~~


You can also display the result from inline chunk 2+5= 7

## Solving least squares


and trying out plotting features:


~~~~{.python}
x = 1:10 + randn(1, 10);
y = linspace(0, 5, length(x));
f = x' \ y';
plot(x , y, 'o')
hold on
plot(x, f*x, 'r')
hold off
~~~~~~~~~~~~~

![](figures/octave_test_figure2_.png)\



And include a plot but hide the code:



![Sinc function](figures/octave_test_figure3_.png)

