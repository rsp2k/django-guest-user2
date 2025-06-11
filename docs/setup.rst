Project Background
==================

This project is a maintained fork of the original `julianwachholz/django-guest-user <https://github.com/julianwachholz/django-guest-user>`_
repository, which appears to be unmaintained (last commit in early 2023). This fork provides:

- 🐛 **Bug fixes** and improvements
- 📦 **Dependency updates** including Django 5.x support
- 🧪 **Expanded testing** across more Python/Django combinations  
- 📚 **Updated documentation**
- 🛠️ **Ongoing maintenance** and issue resolution

The project builds on the excellent foundation laid by Julian Wachholz and the original 
`django-lazysignup <https://github.com/danfairs/django-lazysignup>`_ by Dan Fairs.

Dependencies
============

This project is thoroughly tested on these setups:

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.1, 4.2, 5.0, 5.1, 5.2, and the main branch

Tested across **27 different combinations** to ensure compatibility and reliability.

.. note::

   Django 5.0+ requires Python 3.10 or higher. For Django 3.2-4.2, all Python 
   versions (3.8-3.12) are supported.

In addition, your Django project should be using :doc:`django:ref/contrib/auth`.

How to install
==============

Install the package from PyPI with your favorite package manager::

   pip install django-guest-user
   # or similar, e.g.
   poetry add django-guest-user

Add the app to your :ref:`django:ref/settings:``installed_apps```
and :ref:`django:ref/settings:``authentication_backends```:

.. code-block:: python

   # settings.py
   INSTALLED_APPS = [
      # ... other apps
      "guest_user",
   ]

   AUTHENTICATION_BACKENDS = [
      "django.contrib.auth.backends.ModelBackend",
      # it should be the last entry to prevent unauthorized access
      "guest_user.backends.GuestBackend",
   ]

Allow guests to convert to registered users by adding the URLs to your :doc:`URLconf<django:topics/http/urls>`:

.. code-block:: python

   # urls.py
   from django.urls import path, include

   urlpatterns = [
      # ... other patterns
      path("guest/", include("guest_user.urls")),
   ]

Last but not least, prepare the guest user table by running migrations::

    python manage.py migrate

Quick Start Example
===================

Once installed, you can start using guest users in your views:

.. code-block:: python

   from guest_user.decorators import allow_guest_user
   from guest_user.functions import is_guest_user

   @allow_guest_user
   def my_view(request):
       # request.user is now always authenticated
       # (either a real user or a temporary guest)
       assert request.user.is_authenticated
       
       if is_guest_user(request.user):
           # Show conversion prompt for guest users
           context = {'show_signup_prompt': True}
       else:
           context = {'show_signup_prompt': False}
       
       return render(request, "my_view.html", context)

Migrating from ``django-lazysignup``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``django-guest-user`` can be used as a drop-in replacement for `django-lazysignup`_.

.. _django-lazysignup: https://github.com/danfairs/django-lazysignup

Given the temporary nature of guest or lazy users, the packages can be replaced
without breaking the functionality of any existing (non-temporary) users.

.. note::

   By uninstalling lazysignup, any current temporary users will lose their
   associated data and be signed out of their session.

The following decorators and template filters need to be replaced by their respective counterparts:

- ``@allow_lazy_user`` ➡️ :func:`@allow_guest_user<guest_user.decorators.allow_guest_user>`
- ``@require_lazy_user`` ➡️ :func:`@guest_user_required<guest_user.decorators.guest_user_required>`
- ``@require_nonlazy_user`` ➡️ :func:`@regular_user_required<guest_user.decorators.regular_user_required>`
- Template filter ``is_lazy_user`` ➡️ :func:`is_guest_user<guest_user.templatetags.guest_user.is_guest_user>`

Migrating from Original ``django-guest-user``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're migrating from the original `julianwachholz/django-guest-user`_ repository
to this maintained fork, the transition should be seamless:

1. **Update your requirements**: No code changes needed, just update the source repository
2. **Version compatibility**: This fork maintains API compatibility
3. **Enhanced features**: You'll get improved Django 5.x support and better testing
4. **Ongoing support**: Active maintenance and issue resolution

.. _julianwachholz/django-guest-user: https://github.com/julianwachholz/django-guest-user

Version Compatibility
======================

This package supports a wide range of Django and Python versions:

.. list-table:: Version Compatibility Matrix
   :header-rows: 1
   :stub-columns: 1

   * - Python
     - Django 3.2
     - Django 4.0
     - Django 4.1
     - Django 4.2
     - Django 5.0
     - Django 5.1
     - Django 5.2
   * - 3.8
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - 3.9
     - ✅
     - ✅
     - ✅
     - ✅
     - ❌
     - ❌
     - ❌
   * - 3.10
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - 3.11
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
   * - 3.12
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅
     - ✅

**Django LTS Support**: Django 5.2 is the current LTS (Long Term Support) version,
supported until April 2028.

Recent Improvements
===================

This maintained fork includes several enhancements over the original:

**Version 0.5.5+ (This Fork)**:

- ✨ Enhanced request parameter support in name generators
- 🔧 Fixed missing dependency issues (requests-oauthlib)
- 🧪 Expanded test matrix covering 27 Python/Django combinations
- 📚 Updated documentation for Django 5.x
- 🛡️ Improved code quality with Black formatting and comprehensive linting
- 🐛 Various bug fixes and stability improvements

**Previous Versions** (Original Repository):

- Basic Django 3.2-4.2 support
- Core guest user functionality
- Foundation for current improvements
