from setuptools import setup

meta = {}
exec(open('./debianbts/version.py').read(), meta)
meta['long_description'] = open('./README.md').read()

setup(
    name='python-debianbts',
    version=meta['__version__'],
    description="Python interface to Debian's Bug Tracking System",
    long_description=meta['long_description'],
    long_description_content_type='text/markdown',
    keywords='debian, soap, bts',
    author='Bastian Venthur',
    author_email='venthur@debian.org',
    url='https://github.com/venthur/python-debianbts',
    license='MIT',
    packages=['debianbts'],
    install_requires=[
        'pysimplesoap',
    ],
    extras_require={
      'dev': [
          'pytest',
          'pytest-cov',
          'flake8',
      ]
    },
    python_requires='>=3.4, <4',
    entry_points={
        'console_scripts': [
            'debianbts = debianbts.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Bug Tracking",
    ],
)
