==============================
Python API Client for Kanboard
==============================

Client library for Kanboard API.

- Author: Frédéric Guillot
- License: MIT

Installation
============

.. code-block:: bash

    python3 -m pip install kanboard


This library is compatible with Python >= 3.7.

Note: **Support for Python 2.7 has been dropped since version 1.1.0.**

On Fedora (36 and later), you can install the package using DNF:

.. code-block:: bash

    dnf install python3-kanboard


Examples
========

Methods and arguments are the same as the JSON-RPC procedures described in the
`official documentation <https://docs.kanboard.org/v1/api/>`_.

Python methods are dynamically mapped to the API procedures: **You must use named arguments**.

By default, calls are made synchronously, meaning that they will block the program until completed.

Creating a new team project
---------------------------

.. code-block:: python

    import kanboard

    kb = kanboard.Client('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')
    project_id = kb.create_project(name='My project')


Authenticate as user
--------------------

.. code-block:: python

    import kanboard

    kb = kanboard.Client('http://localhost/jsonrpc.php', 'admin', 'secret')
    kb.get_my_projects()

Create a new task
-----------------

.. code-block:: python

    import kanboard

    kb = kanboard.Client('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')
    project_id = kb.create_project(name='My project')
    task_id = kb.create_task(project_id=project_id, title='My task title')

Use a personalized user agent
-----------------------------

.. code-block:: python

    import kanboard

    kb = kanboard.Client(url='http://localhost/jsonrpc.php',
                         username='admin',
                         password='secret',
                         user_agent='My Kanboard client')

SSL connection and self-signed certificates
===========================================

Example with a valid certificate:

.. code-block:: python

    import kanboard

    kb = kanboard.Client('https://example.org/jsonrpc.php', 'admin', 'secret')
    kb.get_my_projects()

Example with a custom certificate:

.. code-block:: python

    import kanboard

    kb = kanboard.Client(url='https://example.org/jsonrpc.php',
                         username='admin',
                         password='secret',
                         cafile='/path/to/my/cert.pem')
    kb.get_my_projects()

Example with a custom certificate and hostname mismatch:

.. code-block:: python

    import kanboard

    kb = kanboard.Client(url='https://example.org/jsonrpc.php',
                         username='admin',
                         password='secret',
                         cafile='/path/to/my/cert.pem',
                         ignore_hostname_verification=True)
    kb.get_my_projects()

Ignore invalid/expired certificates and hostname mismatches, which will make your application vulnerable to man-in-the-middle (MitM) attacks:

.. code-block:: python

    import kanboard

    kb = kanboard.Client(url='https://example.org/jsonrpc.php',
                         username='admin',
                         password='secret',
                         insecure=True)
    kb.get_my_projects()

Asynchronous I/O
================

The client also exposes async/await style method calls. Similarly to the synchronous calls (see above),
the method names are mapped to the API methods.

To invoke an asynchronous call, the method name must be appended with ``_async``. For example, a synchronous call
to ``create_project`` can be made asynchronous by calling ``create_project_async`` instead.

.. code-block:: python

    import asyncio
    import kanboard

    kb = kanboard.Client('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')

    loop = asyncio.get_event_loop()
    project_id = loop.run_until_complete(kb.create_project_async(name='My project'))


.. code-block:: python

    import asyncio
    import kanboard

    async def call_within_function():
        kb = kanboard.Client('http://localhost/jsonrpc.php', 'jsonrpc', 'your_api_token')
        return await kb.create_project_async(name='My project')

    loop = asyncio.get_event_loop()
    project_id = loop.run_until_complete(call_within_function())


See the `official API documentation <https://docs.kanboard.org/v1/api/>`_ for the complete list of
methods and arguments.
