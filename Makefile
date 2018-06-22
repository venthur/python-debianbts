.PHONY: \
    test \
    lint \
    release \
    clean

all: lint test

test:
	pytest \
	    --cov=debianbts \
	    --cov-branch \
	    --cov-report=term-missing

lint:
	flake8 debianbts tests

release:
	python3 setup.py sdist bdist_wheel upload

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
