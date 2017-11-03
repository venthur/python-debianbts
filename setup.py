from setuptools import setup

exec(open('./debianbts/version.py').read())

setup(
    name='python-debianbts',
    version=__version__,
    description="Python interface to Debian's Bug Tracking System",

    long_description="This package provides the debianbts module, which allows to query Debian's Bug Tracking System.",
    keywords='debian, soap, bts',
    author='Bastian Venthur',
    author_email='venthur@debian.org',
    url='https://github.com/venthur/python-debianbts',
    license='GPL2',
    packages=['debianbts'],
    install_requires=['pysimplesoap'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    entry_points={
        'console_scripts': [
            'debianbts = debianbts.__main__:main'
        ]
    },
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
