==============================
Python API Client for Kanboard
==============================

.. image:: https://travis-ci.org/kanboard/python-api-client.svg?branch=master
    :target: https://travis-ci.org/kanboard/python-api-client

Client library for Kanboard API.

- Author: Frédéric Guillot
- License: MIT

Installation
============

.. code-block:: bash

    pip install kanboard


This library is compatible with Python 2.7, 3.4, 3.5, 3.6, and 3.7.

Examples
========

Methods and arguments are the same as the JSON-RPC procedures described in the `official documentation <https://docs.kanboard.org/en/latest/api/index.html>`_.

Python methods are dynamically mapped to the API procedures. You must use named arguments.

Create a new team project
-------------------------

.. code-block:: python

    from kanboard import Kanboard

    kb = Kanboard('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')
    project_id = kb.create_project(name='My project')


Authenticate as user
--------------------

.. code-block:: python

    from kanboard import Kanboard

    kb = Kanboard('http://localhost/jsonrpc.php', 'admin', 'admin')
    kb.get_my_projects()

Create a new task
-----------------

.. code-block:: python

    from kanboard import Kanboard

    kb = Kanboard('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')
    project_id = kb.create_project(name='My project')
    task_id = kb.create_task(project_id=project_id, title='My task title')

See the `official API documentation <https://docs.kanboard.org/en/latest/api/index.html>`_ for the complete list of methods and arguments.
