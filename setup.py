#!/usr/bin/env python

from distutils.core import setup

setup(name="python-debianbts",
#        version="foo",
        description="Python interface to Debians Bug Tracking System",
        author="Bastian Venthur",
        author_email="venthur@debian.org",
        py_modules=["debianbts"],
        package_dir={"": "src"},
        )

