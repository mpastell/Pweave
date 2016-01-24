# -*- coding: utf-8 -*-

from . import bootstrap
from . import cerulean
from . import skeleton
from . import journal

bootstrap = bootstrap.css
cerulean = cerulean.css
skeleton = skeleton.css
journal = journal.css

pweave = u"""
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
"""
