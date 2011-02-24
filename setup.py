from distutils.core import setup

setup(
    name='python-debianbts',
    version='1.10',
    description='Python interface to Debians Bug Tracking System',
    keywords='debian, soap, bts',
    author='Bastian Venthur',
    author_email='venthur@debian.org',
    url='https://github.com/venthur/python-debianbts',
    license='GPL2',
    package_dir = {'': 'src'},
    py_modules = ['debianbts'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Software Development :: Bug Tracking",
    ],
)
