=====
Rest-Accounts
=====

Rest-Accounts is a simple app to handle REST implementation of `Django <https://www.djangoproject.com/>`_ authentication
system. **rest-accounts** library provides a set of `Django Rest Framework <http://www.django-rest-framework.org/>`_
views to handle basic actions such as create-user, create-token,password
reset and account activation.

Detailed documentation is in the "docs" directory.

Requirements
============

To be able to run **rest-accounts** you have to meet following requirements:

- Python (3.5, 3.6)
- Django (2.0,2.1)
- Django REST Framework (3.7, 3.8)


Installation
============

Simply install using ``pip``:

.. code-block:: bash

    $ pip install rest-accounts


Quick start
-----------


1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'accounts',
    ]


2. Include the polls URLconf in your project urls.py like this::

    path('accounts/', include('accounts.urls')),


3. Start the development server::

	python manage.py runserver,


4. Manage your accounts