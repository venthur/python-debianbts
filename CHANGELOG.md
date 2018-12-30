# Changelog

## [2.8.0] - 2018-12-30

* Added HTTP/S proxy support
* Changed license to MIT
* Improved packaging
* Dropped Python 3.3 support
* Moved from nose to pytest and updated the tests accordingly
* Run linter on tests as well
* Fixed several unicode related tests
* Fixed several linter problems
* Improved parsing of emails on `get_bug_log`

## [2.7.3] - 2018-06-17

* Added Makefile
* Added flake8 to test
* excluded version 1.16.2 pysimplesoap as it is buggy
  See: https://github.com/pysimplesoap/pysimplesoap/issues/167

## [2.7.2] - 2018-02-17

* Minor fix in __main__.py

## [2.7.1] - 2017-11-03

* Fix python_requires

## [2.7.0] - 2017-11-03

* Added Changelog
* Updated packaging
* Added basis for CLI
* Added Travis CI
* Added LICENSE file
* Added long description
* Prevent `None` prefix in `SOAPAction`
* Replaced deprecated assertX methods
* Some whitespace fixes

## [2.6.3] - 2017-09-17
