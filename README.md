Python API Client for Kanboard
==============================

Minimalist Kanboard Python client.

- Author: Frédéric Guillot
- License: MIT

Installation
------------

```bash
pip install kanboard
```

The library is compatible with Python 2 and Python 3.

Examples
--------

The methods and arguments are the same as the JSON-RPC procedures described in the [official documentation](http://kanboard.net/documentation/api-json-rpc).

Python methods are dynamically mapped to the API procedures. You must use named arguments.

### Create a new team project

```python
from kanboard import Kanboard

kb = Kanboard("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token")
project_id = kb.create_project(name="My project")
```

### Authenticate as user

```python
from kanboard import Kanboard

kb = Kanboard("http://localhost/jsonrpc.php", "admin", "admin")
kb.get_my_projects()
```

### Create a new task

```python
from kanboard import Kanboard

kb = Kanboard("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token")
project_id = kb.create_project(name="My project")
task_id = kb.create_task(project_id=project_id, title="My task title")
```

See the [official API documentation](http://kanboard.net/documentation/api-json-rpc) for the complete list of methods and arguments.
