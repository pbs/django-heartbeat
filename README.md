# django-heartbeat  [![Build Status](https://travis-ci.org/pbs/django-heartbeat.svg?branch=master)](https://travis-ci.org/pbs/django-heartbeat) [![PyPI version](https://badge.fury.io/py/django-heartbeat.svg)](https://badge.fury.io/py/django-heartbeat)

Django-heartbeat is a simple reusable app that checks and lists various information
about your project and its dependencies

# Requirements

* Python >=2.7 (tested with Python 2.7, 3.2, 3.3, 3.4, 3.5)
* Django >=1.6

# Installation

Install using pip:
```
pip install django-heartbeat
```

Next, add 'heartbeat' to your settings.py INSTALLED_APPS:
```
INSTALLED_APPS = (
  ...
  'heartbeat',
)
```

Configure urls.py

```Python
if 'heartbeat' in settings.INSTALLED_APPS:
  from heartbeat.urls import urlpatterns as heartbeat_urls

  urlpatterns += [
    url(r'^heartbeat/', include(heartbeat_urls))
  ]
```

# Usage
- `/heartbeat/`

  After this point you can access the /heartbeat/ endpoint and receive a 200 OK.


- `/heartbeat/1337/`

  If you want a more detailed view of some custom checkers you MUST configure a
custom profile for heartbeat in your settings.py. The profile should be
a dictionary containing at least the basic auth credentials or the key `disable`
set to `True` to disable basic authentication.

e.g.:

  ```Python
  HEARTBEAT = {
      'package_name': 'foo_project',
      'checkers': [
          'heartbeat.checkers.build_version',
          'heartbeat.checkers.distribution_list',
          'heartbeat.checkers.debug_mode',
          'heartbeat.checkers.redis_status',
      ],
      'auth': {
          'username': 'foo',
          'password': 'bar',
      },
  }
  ```

If no checkers are defined, heartbeat will default to the following:
- `heartbeat.checkers.distribution_list`
- `heartbeat.checkers.debug_mode`
- `heartbeat.checkers.python_version`


# Available checkers

`heartbeat.checkers.build_version`
  - lists information about installed package
  - Please be aware that in order for this checker to work you have to add the
  'package_name': 'foo_package' key, value pair in the HEARTBEAT settings

`heartbeat.checkers.databases`
  - displays information about the connection with your configured databases

`heartbeat.checkers.debug_mode`
  - displays whether the DEBUG mode is set to True or False

`heartbeat.checkers.distribution_list`
  - lists all installed dependencies
  
`heartbeat.checkers.host`
  - displays various information about your system
  (e.g. hostname, number of CPUs, uptime, used/free memory, etc.)

`heartbeat.checkers.memcached`
  - displays stats about your Memcached.
  - Before enabling this checker please make sure that you have installed the appropriate Memcached binding (the two most common are [python-memcached](https://pypi.python.org/pypi/python-memcached) and [pylibmc](https://pypi.python.org/pypi/pylibmc))

`heartbeat.checkers.python_version`
  - lists the current python version

`heartbeat.checkers.redis_status`
  - checks your connection with the Redis server
  - Make sure that you have CACHEOPS_REDIS configured properly in your settings.py




# Implementing your own checker
- my_checker.py:
  ```Python
  def check(request):
    """
    :param request: HttpRequest object
    :return: dict
    """

    # Checker logic goes here

    return {'ping': 'pong'}
  ```
Note: The function name of your checker MUST be 'check' and has to return a JSON-serializable object

- add it to the settings.HEARTBEAT config
  ```Python
  HEARTBEAT = {
      'checkers': [
          'heartbeat.checkers.distribution_list',
          'my_project.my_checker'
          ...

      ],
      ...
  }
  ```

Simple, huh?

If you would like to contribute to this library with a new checker(or any other
functionality), feel free to make a pull request.


# Contributors
- Andrei Prădan
- Dan Claudiu Pop
