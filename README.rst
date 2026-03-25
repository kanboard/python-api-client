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


- This library is compatible with Python >= 3.9.

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

    with kanboard.Client("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token") as kb:
        project_id = kb.create_project(name="My project")


Authenticate as user
--------------------

.. code-block:: python

    import kanboard

    with kanboard.Client("http://localhost/jsonrpc.php", "admin", "secret") as kb:
        kb.get_my_projects()

Use a custom authentication header
-----------------------------------

If your Kanboard instance uses a custom authentication header
(for example, ``define('API_AUTHENTICATION_HEADER', 'X-My-Custom-Auth-Header');``
in your Kanboard configuration):

.. code-block:: python

    import kanboard

    with kanboard.Client(url="http://localhost/jsonrpc.php",
                         username="demo",
                         password="secret",
                         auth_header="X-My-Custom-Auth-Header") as kb:
        kb.get_me()

Create a new task
-----------------

.. code-block:: python

    import kanboard

    with kanboard.Client("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token") as kb:
        project_id = kb.create_project(name="My project")
        task_id = kb.create_task(project_id=project_id, title="My task title")

Use a personalized user agent
-----------------------------

.. code-block:: python

    import kanboard

    with kanboard.Client(url="http://localhost/jsonrpc.php",
                         username="admin",
                         password="secret",
                         user_agent="My Kanboard client") as kb:
        kb.get_my_projects()

Request timeout
---------------

By default, requests time out after 30 seconds. You can change this with the
``timeout`` parameter (in seconds), or set it to ``None`` to disable the timeout:

.. code-block:: python

    import kanboard

    # Custom 60-second timeout
    with kanboard.Client(url="http://localhost/jsonrpc.php",
                         username="admin",
                         password="secret",
                         timeout=60) as kb:
        kb.get_my_projects()

Error handling
--------------

The client raises ``kanboard.ClientError`` for API errors, network failures,
and malformed responses:

.. code-block:: python

    import kanboard

    with kanboard.Client("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token") as kb:
        try:
            kb.create_project(name="My project")
        except kanboard.ClientError as e:
            print(e)

SSL connection and self-signed certificates
===========================================

Example with a valid certificate:

.. code-block:: python

    import kanboard

    with kanboard.Client("https://example.org/jsonrpc.php", "admin", "secret") as kb:
        kb.get_my_projects()

Example with a custom certificate:

.. code-block:: python

    import kanboard

    with kanboard.Client(url="https://example.org/jsonrpc.php",
                         username="admin",
                         password="secret",
                         cafile="/path/to/my/cert.pem") as kb:
        kb.get_my_projects()

Example with a custom certificate and hostname mismatch:

.. code-block:: python

    import kanboard

    with kanboard.Client(url="https://example.org/jsonrpc.php",
                         username="admin",
                         password="secret",
                         cafile="/path/to/my/cert.pem",
                         ignore_hostname_verification=True) as kb:
        kb.get_my_projects()

.. warning::

    Setting ``insecure=True`` disables all certificate validation and hostname
    checks, making your application vulnerable to man-in-the-middle (MitM) attacks:

.. code-block:: python

    import kanboard

    with kanboard.Client(url="https://example.org/jsonrpc.php",
                         username="admin",
                         password="secret",
                         insecure=True) as kb:
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

    async def main():
        with kanboard.Client("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token") as kb:
            project_id = await kb.create_project_async(name="My project")
            print(project_id)

    asyncio.run(main())


See the `official API documentation <https://docs.kanboard.org/v1/api/>`_ for the complete list of
methods and arguments.
