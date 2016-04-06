#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


setup(
    name='django-heartbeat',
    version='1.0.9',
    description="Your project's heartbeat/healthcheck and dependency status",
    long_description=('A simple reusable app that checks and lists '
                      'various information about your project and its '
                      'dependencies'),
    keywords="django heartbeat health check dependency services status",
    author='PBS Core Services Test Engineers',
    author_email='andrei.pradan@3pillarglobal.com',
    url='https://github.com/pbs/django-heartbeat/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.6,<1.9',
        'psutil==4.0.0',
    ]
)
