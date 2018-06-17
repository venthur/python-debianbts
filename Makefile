.PHONY: \
    test \
    lint \
    release \
    clean

all: lint test

test:
	nosetests \
	    --with-coverage \
	    --cover-branches \
	    --cover-package=debianbts

lint:
	flake8 debianbts

release:
	python3 setup.py sdist bdist_wheel upload

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
