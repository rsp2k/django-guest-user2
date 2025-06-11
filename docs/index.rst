django-guest-user
=================

.. image:: https://github.com/rsp2k/django-guest-user/actions/workflows/lint.yml/badge.svg
   :target: https://github.com/rsp2k/django-guest-user/actions/workflows/lint.yml
   :alt: Code Lint

.. image:: https://github.com/rsp2k/django-guest-user/actions/workflows/test.yml/badge.svg
   :target: https://github.com/rsp2k/django-guest-user/actions/workflows/test.yml
   :alt: Python Tests

.. image:: https://badge.fury.io/py/django-guest-user.svg
   :target: https://badge.fury.io/py/django-guest-user
   :alt: PyPI version

A modern, reusable `Django`_ app that allows site visitors to interact with your project
as if they were registered users without having to sign up first.

.. _Django: https://www.djangoproject.com/

✨ **Zero-friction onboarding** for your users with automatic guest account creation.

Anonymous visitors who request a decorated page get a real temporary user object
assigned and are logged in automatically.

By allowing these guests to use all features of your page, the barrier to entry
is lowered and conversion rates for new users can increase. Visitors will
be more invested in your service and more likely to convert if they already made
progress and created content using your application.

Converting to a permanent user takes very few clicks and allows visitors to save
their progress and don't risk to lose it once the guest users are cleaned up.

.. note::

   **Fork Notice**: This repository is a maintained fork of the original 
   `julianwachholz/django-guest-user <https://github.com/julianwachholz/django-guest-user>`_
   project, which appears to be unmaintained (last updated in early 2023). 
   This fork provides ongoing maintenance, bug fixes, dependency updates, 
   and expanded Django/Python version support.

Key Features
------------

- 🚀 **Zero-friction onboarding**: Visitors can start using your app immediately
- 🔄 **Seamless conversion**: Easy upgrade from guest to registered user  
- 🧹 **Automatic cleanup**: Built-in management commands for guest user cleanup
- 🛡️ **Production ready**: Comprehensive test suite across Python/Django versions
- 📚 **Well documented**: Complete documentation and examples
- 🎯 **Modern codebase**: Built for current Django and Python versions

Compatibility
-------------

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.1, 4.2, 5.0, 5.1, 5.2

Tested across **27 different combinations** to ensure compatibility and reliability.

Project History
---------------

This project builds on a strong foundation:

1. **Original inspiration**: `django-lazysignup`_ by Dan Fairs
2. **Previous iteration**: `julianwachholz/django-guest-user`_ - rewritten for modern Django/Python
3. **Current fork**: `rsp2k/django-guest-user`_ - ongoing maintenance and improvements

.. _django-lazysignup: https://github.com/danfairs/django-lazysignup
.. _julianwachholz/django-guest-user: https://github.com/julianwachholz/django-guest-user
.. _rsp2k/django-guest-user: https://github.com/rsp2k/django-guest-user

This maintained fork provides:

- ✨ **Bug fixes and improvements** 
- 🔄 **Dependency updates** (including Django 5.x support)
- 🧪 **Expanded testing** across more Python/Django combinations
- 📚 **Updated documentation** 
- 🛠️ **Ongoing maintenance** and issue resolution

Quick links
-----------

- `PyPI Package <https://pypi.org/project/django-guest-user/>`_
- `GitHub Repository <https://github.com/rsp2k/django-guest-user>`_
- `5 Steps Quickstart <https://github.com/rsp2k/django-guest-user#-quick-start>`_
- `How to Contribute <https://github.com/rsp2k/django-guest-user/blob/main/CONTRIBUTING.md>`_
- `Issues & Support <https://github.com/rsp2k/django-guest-user/issues>`_

Getting Started
---------------

Install from PyPI::

    pip install django-guest-user

Add to your Django settings and start using guest users in just a few steps.
See the :doc:`setup` guide for detailed instructions.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   setup
   usage
   integrations
   advanced
   config
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
