#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Fedor Baart",
    author_email='fedor.baart@deltares.nl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Service from Rijkswaterstaat for distributing water quantity data.",
    entry_points={
        'console_scripts': [
            'ddlpy=ddlpy.cli:cli',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='ddlpy',
    name='rws-ddlpy',
    packages=find_packages(include=['ddlpy']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SiggyF/ddlpy',
    version='0.1.0',
    zip_safe=False,
)
