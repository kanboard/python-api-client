==============================
Python API Client for Kanboard
==============================

Client library for Kanboard API.

- Author: Frédéric Guillot
- License: MIT

Installation
============

.. code-block:: bash

    pip install kanboard


This library is compatible with Python >= 3.5.

Note: **Support for Python 2.7 has been dropped from version 1.1.0.**

Examples
========

Methods and arguments are the same as the JSON-RPC procedures described in the
`official documentation <https://docs.kanboard.org/en/latest/api/index.html>`_.

Python methods are dynamically mapped to the API procedures. **You must use named arguments.**

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


See the `official API documentation <https://docs.kanboard.org/en/latest/api/index.html>`_ for the complete list of
methods and arguments.
