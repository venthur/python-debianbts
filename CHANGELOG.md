# Changelog

## [4.1.0] - 2024-05-07

* replaced pysimplesoap with hand-coded SOAP requests and parsing of replies
* replaced sphinx with mkdocs
* fixed some documentation issues
* Added Python 3.12 to test suite

## [4.0.2] - 2023-10-22

* distribute typing information using py.typed
* replaced flake8 with ruff
* raised minimum python version to 3.8

## [4.0.1] - 2022-12-08

* switched from setup.py to pyproject.toml
* modernized github actions
* added test for release

## [4.0.0] - 2022-11-19

* removed support for positional arguments in `get_status`, `get_usertags` and
  `get_bugs` (deprecated since 2.10.0 (2019-11))
* added type hints and mypy (strict) to test suite
* updated docstrings to use type hints
* removed obsolete code to fix issue with pysimplesoap with httplib2 for python
  versions < 3.4
* removed support for ancient versions of pysimplesoap < 1.16.2
* updated github actions

## [3.2.4] - 2022-11-02

* scrubbed obsolete constraints since debian/buster
* updated dev-requirements
* dropped python 3.6 support

## [3.2.3] - 2022-06-29

* bumped version to allow for source-only upload in debian (no changes)

## [3.2.2] - 2022-06-26

* test against Python 3.10
* reformatted code
* updated dependencies
* added dependabot github action

## [3.2.1] - 2022-04-04

* Added sphinx documentation
* Updated build system
* Use pytest-xdist to speed up testing

## [3.2.0] - 2021-08-07

* Allow to change the default SOAP location

## [3.1.0] - 2020-12-18

* Changed from FeedParser to BytesFeedParser with STMP policy in
  `get_bug_logs`
* Document and test the `archive` kwarg of `get_bugs`
* Migrated from TravisCI to GitHub workflows

## [3.0.1] - 2019-11-13

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
