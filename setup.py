#!/usr/bin/env python

import os

from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()


def get_packages(package):
    return [
        dirpath for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


setup(
    name='rest-accounts',
    version='0.1',
    packages=get_packages('accounts'),
    license='MIT',
    author='loganathan',
    description='Django Rest Authentication System',
    author_email='loganathanengrr@gmail.com',
    long_description=readme,
    install_requires=['django-templated-mail'],
    include_package_data=True,
    url='https://github.com/loganathanengrr/rest-accounts',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)