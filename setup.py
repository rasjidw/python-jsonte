#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'python-dateutil',
    'sdag2',
    'six'
]

test_requirements = [
]

setup(
    name='jsonte',
    version='0.8.5',
    description="A simple way of 'extending' json to support additional types like datetime, Decimal and binary data.",
    long_description=readme + '\n\n' + history,
    author="Rasjid Wilcox",
    author_email='rasjidw@openminddev.net',
    url='https://github.com/rasjidw/python-jsonte',
    py_modules=['jsonte'],
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='jsonte json',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='test_jsonte',
    tests_require=test_requirements
)
