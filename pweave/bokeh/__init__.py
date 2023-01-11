from IPython.display import display_html

try:
    from bokeh.embed import components
    from bokeh.resources import CDN
except ImportError:
    pass


def dedent(text):
    return "\n".join([line.lstrip() for line in text.splitlines()])


def output_pweave():
    """
    Call this once in a Pweave document to include correct
    headers for Bokeh. Analogous to Bokeh's output_notebook
    """
    out = CDN.render_css()
    out += CDN.render_js()
    # display_markdown(out, raw=True)
    display_html(out, raw=True)


def show(plot):
    """
    Include a Bokeh figure in Pweave document. Use This
    instead of ``bokeh.plotting.show``. Provides html output.

    :param plot: ``bokeh.plotting.figure`` plot to include in output.
    """

    script, div = components(plot)
    out = script
    out += div
    # Pandoc only works if indent is removed
    # Need to display as same output, not separate, otherwise md2hml show 2 figs
    # display_markdown(dedent(out), raw=True)
    display_html(out, raw=True)
