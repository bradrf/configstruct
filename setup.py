#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'future>=0.15.2',
    'configparser>=3.5.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='configstruct',
    version='0.1.0',
    description="Simplified configuration and settings management library.",
    long_description=readme + '\n\n' + history,
    author="Brad Robel-Forrest",
    author_email='brad@bitpony.com',
    url='https://github.com/bradrf/configstruct',
    packages=[
        'configstruct',
    ],
    package_dir={'configstruct':
                 'configstruct'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='configstruct',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
