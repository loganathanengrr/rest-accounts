=====
Accounts
=====

Accounts is a simple rest impplementation of django authentication system. resta accounts manage the following basic action create-token,refresh-token,verify-token ,change-username,password-change,password-reset,get-login-user

Detailed documentation is in the "docs" directory.

Requirements

To be able to run djoser you have to meet following requirements:

Python (3.5, 3.6)
Django (2.0,2.1)
Django REST Framework (3.8)


Installation
-----------
	pip install rest-accounts

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