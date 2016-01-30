from __future__ import print_function, division, absolute_import, unicode_literals

htmltemplate = {}

htmltemplate["header"] = \
"""
<!DOCTYPE html>
<HTML>
<HEAD>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<script type="text/x-mathjax-config">
    MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/LaTeX", "output/HTML-CSS"],
    "HTML-CSS": { availableFonts: ["TeX"] }
    });
</script>

<script type="text/javascript"
    src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>

<style>
%(theme_css)s
</style>

<style>
%(pygments_css)s
</style>

<style>
h1.title {margin-top : 20px}
img {max-width : 100%%}
</style>

</HEAD>
<BODY>
    <div class ="container">
        <div class = "row">
            <div class = "col-md-12 twelve columns">
"""

htmltemplate["footer"]="""
    <HR/>
    <div class="footer">
      <p>Published from <a href="%(source)s">%(source)s</a>
    using <a href="http://mpastell.com/pweave">Pweave</a> %(version)s
    on %(time)s.<p></div>

            </div>
        </div>
    </div>
  </BODY>
</HTML>
"""
