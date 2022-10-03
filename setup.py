#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

requires = [
    'Django>=1.6',
    'psutil',
]

if sys.version_info < (3, 3, 0):
    requires.append('py2-ipaddress>=3.4.0')

setup(
    name='django-heartbeat',
    version='2.1.0',
    description="Your project's heartbeat/healthcheck and dependency status",
    long_description=('A simple reusable app that checks and lists '
                      'various information about your project and its '
                      'dependencies'),
    keywords="django heartbeat health check dependency services status",
    author='PBS Core Services',
    author_email='pbsi-team-core-services@pbs.org',
    url='https://github.com/pbs/django-heartbeat/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires
)
