
# Octave test document for pweave

You can use inline code chunks like in Python documents:

Give y value 300  in hidden chunk.

And let's verify that it worked:


{line-numbers=off}
~~~~~~~~
y
~~~~~~~~

{line-numbers=off}
~~~~~~~~
y =  300

~~~~~~~~



You can also display the result from inline chunk 2+5= 7

## Solving least squares and trying out plotting features:


{line-numbers=off}
~~~~~~~~
x = 1:10 + randn(1, 10);
y = linspace(0, 5, length(x));
f = x' \ y';
plot(x , y, 'o')
hold on
plot(x, f*x, 'r')
hold off
~~~~~~~~

![](figures/octave_test_figure2_.png)


And include a plot but hide the code:


![Sinc function](figures/octave_test_figure3_.png)

