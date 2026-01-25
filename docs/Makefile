# Makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
SOURCEDIR     = source
BUILDDIR      = _build

# The paper size ('letter' or 'a4').
ifeq ($(PAPER),)
PAPER=a4
endif

# The paper size for PDF output only.
PAPEROPT_letter = -D latex_paper_size=letter
PAPEROPT_a4 = -D latex_paper_size=a4
ALLSPAPEROPTS = $(PAPEROPT_$(PAPER))

# the i18n builder cannot share the same DOCTREES as the others
SPHINXOPTS += $(PAPEROPT_$(PAPER))

# all py files except those with leading underscores
PYSOURCEFILES = $(shell find . -type f -name '*.py' ! -name '_*')

.PHONY: help clean html dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf text man changes linkcheck doctest coverage gettext
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  dirhtml    to make HTML files named index.html in directories"
	@echo "  singlehtml to make a single large HTML file"
	@echo "  pickle     to make pickle files"
	@echo "  json       to make JSON files"
	@echo "  htmlhelp   to make HTML files and a HTML help project"
	@echo "  qthelp     to make HTML files and a Qt help project"
	@echo "  devhelp    to make HTML files as a Qt DevHelp project"
	@echo "  epub       to make an EPUB file"
	@echo "  latex      to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
	@echo "  latexpdfja to make LaTeX files and run them through platex and dvipdfmx"
	@echo "  text       to make text files"
	@echo "  man        to make man pages"
	@echo "  texinfo    to make Texinfo files"
	@echo "  info       to make Texinfo files and build the info"
	@echo "  gettext    to make .pot files. The default action is `in place'"
	@echo "  changes    to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck  to make a link check of all external links"
	@echo "  doctest    to make sure the code examples in the docstrings are up to date"
	@echo "  coverage   to check how much of the documentation is covered by tests"

clean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPAPEROPTS) $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML files are in $(BUILDDIR)/html."

dirhtml:
	$(SPHINXBUILD) -b dirhtml $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML files are in $(BUILDDIR)/dirhtml."

singlehtml:
	$(SPHINXBUILD) -b singlehtml $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML files are in $(BUILDDIR)/singlehtml."

pickle:
	$(SPHINXBUILD) -b pickle $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/pickle
	@echo
	@echo "Build finished. The pickle files are in $(BUILDDIR)/pickle."

json:
	$(SPHINXBUILD) -b json $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/json
	@echo
	@echo "Build finished. The HTML files are in $(BUILDDIR)/json."

htmlhelp:
	$(SPHINXBUILD) -b htmlhelp $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/htmlhelp
	@echo
	@echo "Build finished. The HTML help files are in $(BUILDDIR)/htmlhelp."

qthelp:
	$(SPHINXBUILD) -b qthelp $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/qthelp
	@echo
	@echo "Build finished. The HTML files are in $(BUILDDIR)/qthelp."

devhelp:
	$(SPHINXBUILD) -b devhelp $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/devhelp
	@echo
	@echo "Build finished. the devhelp files are in $(BUILDDIR)/devhelp."

epub:
	$(SPHINXBUILD) -b epub $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latex:
	$(SPHINXBUILD) -b latex $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/latex
	@echo
	@echo "Build finished. The LaTeX files are in $(BUILDDIR)/latex."

latexpdf:
	$(SPHINXBUILD) -b latex $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/latex
	@echo "Running LaTeX files through pdflatex..."
	-$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; see $(BUILDDIR)/latex/latex.pdf."

latexpdfja:
	$(SPHINXBUILD) -b latex $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/latex
	@echo "Running LaTeX files through platex and dvipdfmx..."
	-$(MAKE) -C $(BUILDDIR)/latex all-pdf-ja
	@echo "pdflatex finished; see $(BUILDDIR)/latex/latex.pdf."

text:
	$(SPHINXBUILD) -b text $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
	$(SPHINXBUILD) -b man $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/man
	@echo
	@echo "Build finished. The man man pages in $(BUILDDIR)/man."

texinfo:
	$(SPHINXBUILD) -b texinfo $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/texinfo
	@echo
	@echo "Build finished. The texinfo files are in $(BUILDDIR)/texinfo."

info:
	$(SPHINXBUILD) -b texinfo $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/texinfo
	-$(MAKE) -C $(BUILDDIR)/texinfo info
	@echo
	@echo "The texinfo files are in $(BUILDDIR)/texinfo."

gettext:
	$(SPHINXBUILD) -b gettext $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/locale
	@echo
	@echo "Build finished. The .pot files are in $(BUILDDIR)/locale."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; see $(BUILDDIR)/linkcheck/html/index.html."

doctest:
	$(SPHINXBUILD) -b doctest $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/doctest
	@echo
	@echo "Testing of doctests in the sources finished, see $(BUILDDIR)/doctest/html/index.html."

coverage:
	$(SPHINXBUILD) -b coverage $(ALLSPAPEROPTS) $(SPHINXOPTS) . $(BUILDDIR)/coverage
	@echo "Testing coverage of documentation finished; see $(BUILDDIR)/coverage/html/index.html."
