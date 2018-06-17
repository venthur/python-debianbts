.PHONY: \
    test \
    lint \
    docs \
    release \
    clean

all: lint test

test:
	nose
#	pytest \
#	    --cov=debianbts \
#	    --cov-branch \
#	    --cov-report=term-missing

lint:
	flake8 debianbts

docs:
	$(MAKE) -C docs html

release:
	python3 setup.py sdist bdist_wheel upload

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
