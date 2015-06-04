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
    'python-dateutil'
]

test_requirements = [
]

setup(
    name='jsonte',
    version='0.8.1',
    description="Json Type Extensions.",
    long_description=readme + '\n\n' + history,
    author="Rasjid Wilcox",
    author_email='rasjidw@openminddev.net',
    url='https://github.com/rasjidw/jsonte',
    packages=[
        'jsonte',
    ],
    package_dir={'jsonte': 'jsonte'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='jsonte',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
