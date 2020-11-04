# Minimal makefile for Sphinx documentation
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
.PHONY: help
help:
	@echo " == simple make == "
	@echo "type 'make clean html' to build documentation file"
	@echo ""
	@echo " == command references == "
	@echo "clean: clean build directory"
	@echo "html: generate html file"

.PHONY: clean
clean:
	-rm -rf $(BUILDDIR)/*

.PHONY: html
html:
	sphinx-build $(SOURCEDIR) ./$(BUILDDIR)
