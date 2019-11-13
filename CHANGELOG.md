# Changelog

## [unreleased]

* Re-organized tests
* Fixed base64 decoding for `done_by`

## [3.0.0] - 2019-11-12

* Dropped Python2 support

## [2.10.0] - 2019-11-01

* Modernized a few awkward method calls:
  * Deprecated support for positional arguments in `get_status`, we use a list
    of bugnumbers explicitly now: `get_status(123, 234, 345)` becomes
    `get_status([123, 234, 345])`
  * Deprecated support for positional arguments in `get_usertags`, we use a
    list of tags explicitly now: 
    `get_usertags('mail@example.com', 'foo', 'bar')` becomes
    `get_usertags('mail@example.com', ['foo', 'bar'])`
  * Deprecated support for positional arguments in `get_bugs`, we use `kwargs`
    explicitly now:
    `get_bugs('package', 'gtk-qt-engine', 'severity', 'normal')` becomes
    `get_bugs(package='gtk-qt-engine', severity='normal')`
  the old ways to call those methods will be supported for a while, but there
  will be deprecation warnings.
* Report coverage for tests as well
* Updated a few tests to increase coverage
* Removed randomness from some tests

## [2.9.0] - 2019-11-01

* Added `done_by` field to Bug Status

## [2.8.2] - 2018-12-31

* Fixed compatibility with pysimplesoap 1.16.2 (patch by Gaetano Guerriero)

## [2.8.1] - 2018-12-30

* Fixed version

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
