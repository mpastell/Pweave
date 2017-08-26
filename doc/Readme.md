# Pweave documentation

This directory contains Pweave documentation sources. You can find the latest published docs from http://mpastell.com/pweave.

## Contributing to the docs

Contributions to the docs are very welcome in order to keep them up to date!
The docs are generated from files in the `source` and `examples` directories.
If there is a matching `.rstw` and `.rst` file in the `source` directory
remember to edit `.rstw` version.

Build the docs using:

```bash
make html
```

Building the docs requires Pweave, Sphinx, LaTex and Pandoc.

You can install the required packages on Ubuntu using:

```bash
pip install sphinx sphinx_rtd_theme
sudo apt-get install texlive texlive-latex-extra texlive-generic-extra pandoc
```
