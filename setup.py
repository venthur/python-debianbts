from distutils.core import setup
import sys

sys.path.insert(0, 'src')

import debianbts


setup(
    name='python-debianbts',
    version=debianbts.__version__,
    description="Python interface to Debian's Bug Tracking System",
    keywords='debian, soap, bts',
    author='Bastian Venthur',
    author_email='venthur@debian.org',
    url='https://github.com/venthur/python-debianbts',
    license='GPL2',
    package_dir={'': 'src'},
    py_modules=['debianbts'],
    install_requires=['pysimplesoap'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Communications",
        "Topic :: Software Development :: Bug Tracking",
    ],
)
