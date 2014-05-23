from __future__ import print_function, division, absolute_import, unicode_literals

from pygments.formatters import HtmlFormatter

htmltemplate =  {}


htmltemplate["header"] = ("""
<HTML>
  <HEAD>



    <script type="text/javascript"
    src="https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
    </script>

    <style>
      body
      {
      max-width : 1000px;
      margin : auto;
      margin-top : 20px;
      font: 14px/21px "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;
      text-align : justify
      }

      h1.title {font-size : 1.6em}

      h1 {font-size : 1.4em}

      h2 {font-size : 1.2em}

      h3 {font-size : 1.1em}

      h1, h2, h3, h4, h5, h6
      {
      color : maroon;
      }

      .highlight
      {
      border-style:solid;
      border-width : 1px;
      border-color : gray;
      padding-left : 5px;
      }

      a
      {
      color : maroon;
      }

      .footer
      {
      font-size : smaller;
      color : gray;
      text-align : right;
      }

      %s

    </style>
  </HEAD>
  <BODY>
""" % HtmlFormatter().get_style_defs())

htmltemplate["footer"] = """
    <HR/>
    <div class="footer">\
      <p>Published from <a href="%(source)s">%(source)s</a> \
	using <a href="http://mpastell.com/pweave">Pweave</a> %(version)s\
	on %(time)s.<p></div>
  </BODY>
</HTML>
"""
