#' % Linear Regression model with Python
#' % Matti Pastell
#' % 19.4.2013

#' #Requirements
#' This en example of doing linear regression analysis using Python 
#' and [statsmodels](http://statsmodels.sourceforge.net/devel/). The 
#' example requires statsmodels > 0.5 and we'll use the new formula API
#' which makes fitting the models very familiar for R users.
#' You'll also need [Numpy](http://www.numpy.org/), [Pandas](http://pandas.pydata.org/)
#' and [matplolib](http://matplotlib.org/).

#' The analysis can be published using the current [Pweave development version](https://bitbucket.org/mpastell/pweave/src).

#' Import libraries

import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt

#' We'll use [whiteside](http://stat.ethz.ch/R-manual/R-patched/library/MASS/html/whiteside.html) dataset from R package MASS. You can read the description of the dataset from the link, but in short it contains:

#' >*The weekly gas consumption and average external temperature at a house in south-east England for two
#' heating seasons, one of 26 weeks before, and one of 30 weeks after cavity-wall insulation was installed.*

#' Read the data from [pydatasets repo](https://github.com/cpcloud/pydatasets) using Pandas:

url = 'https://raw.github.com/cpcloud/pydatasets/master/datasets/MASS/whiteside.csv'
whiteside = pd.read_csv(url)

#' # Fitting the model
#' Let's see what the relationship between the gas consumption is before the insulation.
#' See [statsmodels documentation](http://statsmodels.sourceforge.net/devel/example_formulas.html)
#' for more information about the syntax.

model = sm.ols(formula='Gas ~ Temp', data=whiteside, subset = whiteside['Insul']=="Before")
fitted = model.fit()
print fitted.summary()

#' # Plot the data and fit

Before = whiteside[whiteside["Insul"] == "Before"]
plt.plot(Before["Temp"], Before["Gas"], 'ro')
plt.plot(Before["Temp"], fitted.fittedvalues, 'b')
plt.legend(['Data', 'Fitted model'])
plt.ylim(0, 10)
plt.xlim(-2, 12)
plt.xlabel('Temperature')
plt.ylabel('Gas')
plt.title('Before Insulation')

#' # Fit diagnostiscs
#' Statsmodels [OLSresults](http://statsmodels.sourceforge.net/devel/generated/statsmodels.regression.linear_model.OLSResults.html) objects contain the usual diagnostic information about the model and you can use the `get_influence()` method to get more diagnostic information (such as Cook's distance).

#' ## A look at the residuals
#' Histogram of normalized residuals

plt.hist(fitted.norm_resid())
plt.ylabel('Count')
plt.xlabel('Normalized residuals')


#' ## Cooks distance

#' [OLSInfluence](http://statsmodels.sourceforge.net/devel/generated/statsmodels.stats.outliers_influence.OLSInfluence.html)
#'  objects contain more diagnostic information 

influence = fitted.get_influence()
#c is the distance and p is p-value
(c, p) = influence.cooks_distance
plt.stem(np.arange(len(c)), c, markerfmt=",")


#' # Statsmodels builtin plots

#' Statsmodels includes a some builtin function for plotting residuals against leverage:

from statsmodels.graphics.regressionplots import *
plot_leverage_resid2(fitted)
influence_plot(fitted)
