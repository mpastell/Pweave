#Code snippets that are executed by subprocess writer

init_matplotlib = """
%matplotlib inline
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('png', 'pdf', 'svg')
import matplotlib
"""
