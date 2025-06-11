[![Code Lint](https://github.com/rsp2k/django-guest-user/actions/workflows/lint.yml/badge.svg)](https://github.com/rsp2k/django-guest-user/actions/workflows/lint.yml)
[![Python Tests](https://github.com/rsp2k/django-guest-user/actions/workflows/test.yml/badge.svg)](https://github.com/rsp2k/django-guest-user/actions/workflows/test.yml)
[![Documentation](https://readthedocs.org/projects/django-guest-user/badge/?style=flat)](https://django-guest-user.readthedocs.io)
[![PyPI version](https://badge.fury.io/py/django-guest-user.svg)](https://badge.fury.io/py/django-guest-user)
[![Python versions](https://img.shields.io/pypi/pyversions/django-guest-user.svg)](https://pypi.org/project/django-guest-user/)
[![Django versions](https://img.shields.io/pypi/djversions/django-guest-user.svg)](https://pypi.org/project/django-guest-user/)

# django-guest-user

Allow visitors to interact with your site like a temporary user ("guest") without requiring registration.

Anonymous visitors who request a decorated page get a real temporary user object assigned and are logged in automatically. They can use the site like a normal user until they decide to convert to a real user account to save their data.

Inspired by and as an alternative for [django-lazysignup](https://github.com/danfairs/django-lazysignup) and rewritten for modern Django and Python versions.

> **📋 Note**: This repository is a fork of [julianwachholz/django-guest-user](https://github.com/julianwachholz/django-guest-user), which appears to be unmaintained. This fork includes bug fixes, dependency updates, expanded Django/Python version support, and ongoing maintenance.

## ✨ Features

- 🚀 **Zero-friction onboarding**: Visitors can start using your app immediately
- 🔄 **Seamless conversion**: Easy upgrade from guest to registered user
- 🧹 **Automatic cleanup**: Built-in management commands for guest user cleanup
- 🛡️ **Production ready**: Comprehensive test suite across Python/Django versions
- 📚 **Well documented**: Complete documentation and examples
- 🎯 **Modern codebase**: Built for current Django and Python versions

## 🔧 Requirements

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.1, 4.2, 5.0, 5.1, 5.2

Tested across **27 different combinations** to ensure compatibility and reliability.

## 📦 Installation

Install from PyPI:

```bash
pip install django-guest-user
```

## ⚡ Quick Start

1. **Add to your Django project:**
   ```python
   # settings.py
   INSTALLED_APPS = [
       # ... your other apps
       'guest_user',
   ]

   AUTHENTICATION_BACKENDS = [
       'django.contrib.auth.backends.ModelBackend',
       'guest_user.backends.GuestBackend',
   ]
   ```

2. **Include URLs:**
   ```python
   # urls.py
   from django.urls import path, include

   urlpatterns = [
       # ... your other URLs
       path('guest/', include('guest_user.urls')),
   ]
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Decorate your views:**
   ```python
   from guest_user.decorators import allow_guest_user

   @allow_guest_user
   def my_view(request):
       # request.user is now always authenticated
       # (either a real user or a temporary guest)
       assert request.user.is_authenticated
       return render(request, "my_view.html")
   ```

That's it! Your visitors can now interact with your app without registration.

## 🎮 Usage Example

```python
from django.shortcuts import render
from guest_user.decorators import allow_guest_user
from guest_user.functions import is_guest_user

@allow_guest_user
def shopping_cart(request):
    if is_guest_user(request.user):
        # Show conversion prompt for guest users
        show_signup_prompt = True
    else:
        show_signup_prompt = False
    
    return render(request, 'cart.html', {
        'show_signup_prompt': show_signup_prompt,
    })
```

## 📚 Documentation

Find the [**complete documentation**](https://django-guest-user.readthedocs.io/) on Read the Docs, including:

- **Installation guide**: Detailed setup instructions
- **Configuration options**: Customize guest user behavior
- **Template tags**: Helper functions for your templates
- **Management commands**: Cleanup and maintenance tools
- **Advanced usage**: Custom name generators, swappable models, and more

## 🧪 Testing & Quality

This project maintains high code quality standards:

- ✅ **Comprehensive testing**: 27 Python/Django version combinations
- ✅ **Code formatting**: Enforced with Black
- ✅ **Linting**: Flake8 with strict rules
- ✅ **Type hints**: Full type annotation coverage
- ✅ **Documentation**: Complete API documentation and examples

## 🤝 Contributing

All contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Set up development environment:**
   ```bash
   git clone your-fork-url
   cd django-guest-user
   pip install poetry
   poetry install
   ```
3. **Run tests:**
   ```bash
   poetry run pytest
   # Or test all environments:
   poetry run tox
   ```
4. **Follow code standards:**
   ```bash
   poetry run black .
   poetry run flake8
   ```

Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## 🔄 Migration from django-lazysignup

If you're migrating from `django-lazysignup`, check our [migration guide](https://django-guest-user.readthedocs.io/en/latest/migration.html) for step-by-step instructions.

## 📈 Development Status

This project is under **active development** with regular updates and improvements. 

### Fork History

This repository is a maintained fork of the original [julianwachholz/django-guest-user](https://github.com/julianwachholz/django-guest-user) project, which appears to be abandoned (last updated in early 2023). This fork provides:

- ✨ **Bug fixes and improvements** 
- 🔄 **Dependency updates** (including Django 5.x support)
- 🧪 **Expanded testing** across more Python/Django combinations
- 📚 **Updated documentation** 
- 🛠️ **Ongoing maintenance** and issue resolution

The core functionality is stable and production-ready, built upon the solid foundation of both [django-lazysignup](https://github.com/danfairs/django-lazysignup) and the original django-guest-user.

**Recent improvements in this fork:**
- ✨ Enhanced request parameter support in name generators
- 🔧 Improved dependency management and testing
- 📚 Updated documentation for Django 5.x
- 🛡️ Expanded test matrix for better compatibility
- 🐛 Fixed missing dependency issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original [django-lazysignup](https://github.com/danfairs/django-lazysignup) project by Dan Fairs
- Original [django-guest-user](https://github.com/julianwachholz/django-guest-user) project by Julian Wachholz
- All the [contributors](https://github.com/rsp2k/django-guest-user/graphs/contributors) who have helped improve this package
