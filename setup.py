#!/usr/bin/env python

from distutils.core import setup

setup(name="python-debianbts",
        version="1.10",
        description="Python interface to Debians Bug Tracking System",
        author="Bastian Venthur",
        author_email="venthur@debian.org",
        py_modules=["debianbts"],
        package_dir={"": "src"},
        )

