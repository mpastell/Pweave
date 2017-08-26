Release notes
-------------

**In 0.30**

* Use IPython kernel to run Python code:

  - support for rich output
  - support IPython magics
  - Improved error handling

* Render tracebacks correctly
* Drop Python 2 support
* Run code using any Jupyter kernel with `--kernel` option
* Output directly to Jupyter notebooks with chunk options preserved
  as metadata -> ability to use custom nbconvert templates in addition to builtin formatters.
* Drop uppercase versions on `pweave` and `ptangle` scripts
* Weave documents from URLs

**In 0.25**

Released 21st, April 2016

* New pweave option: `output` allows to set the output file
* New better themes for pypublish and an option to choose theme
* New output format: softcover (https://www.softcover.io/)


**In 0.24**

Released 20th, January 2016

* New input format: markdown
* New supported script format: Spyder cell markup
* Support new link attributes for pandoc >= 1.16
* pypublish now embeds figures in html output
* pypublish no longer defaults to wrap = False in html output
* Improved test coverage
* More robust script reader, not sensitive to empty lines anymore
* Removed obsolete Julia support.

**In 0.23.2**

Released 16th, January 2016

* Add --latex_engine option to pypublish. Enables the use xetex or luatex
* Bug fixes
  - Fix formatting bugs for eval=FALSE #18
  - Fix white space error in code chunks for wrap = FALSE #24
  - Fix unicode bug with pypublish #21
  - Update pypublish template to include textcomp due to changes in Pandoc #23

**In 0.23.1**

Released 12th, January 2016

* Fix for multiline indented blocks by @abukaj
* Pypublish missing \begin{document} problem fixed by @abukaj
* Fix for pandoc 1.14 - \tightlist not defined @trsaunders

**In 0.23**

Released 7th, December 2014

* New Python option --shell eshell, runs python as subprocess and is not affected by Pweave imports.
* Pweave can now be used to weave Octave, Matlab and Julia code using --shell option. Have a look at the examples on Github

**0.22.2**

Released 14th, November 2014

* Figure and cache directory are now handled relative to weaved document
* Fixed caching
* Improved error reporting and exception handling

**0.22.1**

Released 14th, November 2014

* Fixed a bug with inline code chunks.


**0.22**

Released 13th, November 2014

* Package global options moved to pweave.rcParams. This is a breaking change if you have used
  Pweb class to modify Pweave options. Should not affect commandline usage.
* Renamed pweave.pweave to pweave.weave, pweave.ptangle to pweave.tangle
* Python 3 compatibilty, Thanks to Grant Goodyear https://github.com/g2boojum
* Publishing of scripts from command line : pypublish script
* Conversion between input formats and markups: Pweave-convert script

  - Convert to IPython notebooks by Aaron O'Leary https://github.com/aaren

* Possibility to run shell code from Pweave. See `engine` chunk option.
* New input formats:

  - Script
  - IPython notebook

* Bugfix: setting figure format from command line fixed.
* Ipython terminal
* Source option for chunks

  - Read from module
  - Read from file

* Multichunk blocks: complete option
* rst format uses `.. codeblock::` python directive for code chunks.
* Output formats:

  - Leanpub markdown

* New options for figures

  - f_size ( (8,6) ) Saved figure size in inches a tuple (w, h)
  - f_env (None) Environment that goes around figure e.g. sidefigure
  - f_spines (True) removes spines from figure right and top if False.
  - complete (False)
  - source: Read chunk source from file or python module or file
  - engine: Choose engine running the code. "python" or "shell"


**0.21.2**

Released 15th, April 2013

- Bug fix: 0.21.1 Failed to build, 0.21.2 now works.


**0.21.1**
Released 12th, April 2013

- Bug fix: Documentation mode was broken in 0.21. It's now
  fixed. *Don't use "is" instead of "==" for strings*. `Stackoverflow
  to rescue again
  <http://stackoverflow.com/questions/2988017/string-comparison-in-python-is-vs>`_ .
- Documentation has been improved a lot see e.g. examples about
  `customizing <customizing.html>`_ and `subclassing <subclassing.html>`_.

**0.21**

Released: 11th, April 2013

- Support for multiple figures in a code chunk
- Users can supply their own classes for formatting output, this makes
  adding own formats easier.
- New chunk option "include" controls if generated figures are
  included in code
- New chunk option wrap will wrap code and results (defaults to True).
- Removed `--minted` command line option, this is now available as
  "texminted" format.
- New default format for minted code block. (Thanks to Thomas Unterthiner)
- New features for latex figures

  * Label is set for figures using code chunks label as fig:label. (Thanks to Matthew McDonald)
  * You can specify postion via f_pos chunk option.

- Bug fixes:

  * Width setting for figures now works.



**0.20.1**

Released: 10th, October 2011

- Included tangling script and function: Ptangle and pweave.ptangle
- Pweave and Ptangle are now .exe files in Windows and can (and must)
  be executed without the .py extension.
- Bug fix: Pweave no longer adds extra line to the start of file ->
  pandoc title blocks work now.

**0.20**

Released: 8th, October 2011

- This is a major release and Pweave is completely restructured
- Pweave is now a library and can be run from the interpreter, this
  has multiple advantages

  * several documents can share same namespace.
  * you can work interactively after running pweave
  * Function pweave.pweave exposes most options, pweave.Pweb class
    makes it possible to customasize the execution and formatting with
    direct access to parsed and executed code before formatting and
    writing.

- You can now embed code in doc chunks using ERB syntax
- Documentation mode caches all results from code chunks so you don't
  need to rerun it when working with doc chunks.
- New format, Pandoc markdown
- New option: use minted with Latex
- Easy to specify new formats using custom dictionary
- Hidden option for results
- Support for capturing `Sho <http://research.microsoft.com/en-us/projects/sho/default.aspx>`_ plots for Ironpython users.
- Bug fixes.

  * chunk start and end detection improved, decorators are working now.
  * term mode now executes chunks with term = False if execution fails.

**0.13**

Released: 3rd, February 2011

- Improved term mode, you can now use for loops etc. indented blocks
  in term mode (Contributed by Tamas Nepusz).
- Code runs in its own environment instead of global environment
  (Contributed by Tamas Nepusz).


**0.12**

Released: 4th, May 2010

-  Added terminal mode for output
-  Figure options: add image caption, making it a figure
-  Small bug fixes to capturing output
-  Documentation: added howto for using `Pweave with
   Emacs <emacs.html>`_ and more complete example

**0.11**

Released: 22th, March 2010

-  Command line option for choosing figure format
-  Figure options: control image width
-  Bug fixes for adding images
-  Pweave now extracts code from the source document


**0.10**

Released: 12th, March 2010

-  Initial release
