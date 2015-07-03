.PHONY: all clean test

all:	clean test

test:
	tox

clean:
	-find . -name "__pycache__" | xargs rm -rf
	-find . -name "*.pyc" | xargs rm -f
	-find . -name '*.egg-info' -type d | xargs rm -rf
	-find . -name '*.egg' -type d | xargs rm -rf
	-rm -rf build
	-rm -rf dist
	-rm -rf docs/_build
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf .tox
	-rm -rf examples/pushrodr/pushrodr.db

