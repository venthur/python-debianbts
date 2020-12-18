VERSION = $(shell python3 setup.py --version)

all: lint test

test:
	pytest
.PHONY: test

lint:
	flake8
.PHONY: lint

release:
	python3 setup.py sdist bdist_wheel
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
.PHONY: release

tarball:
	git archive --output=../python-debianbts_$(VERSION).orig.tar.gz HEAD

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
	rm -rf htmlcov
.PHONY: clean
