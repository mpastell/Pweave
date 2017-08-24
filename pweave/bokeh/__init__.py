from IPython.display import display_html, display_markdown
from bokeh.resources import CDN
from bokeh.embed import components

def dedent(text):
    return "\n".join([line.lstrip() for line in text.splitlines()])

def output_pweave():
    out = CDN.render_css()
    out += CDN.render_js()
    display_markdown(out, raw=True)
    display_html(out, raw=True)

def show(plot):
    script, div = components(plot)
    out = script
    out+= div
    #Pandoc only works if indent is removed
    display_markdown(dedent(out), raw=True)
    display_html(out, raw=True)
