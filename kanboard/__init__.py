"""
Kanboard API client

Minimalist Kanboard API client.

Example:

    from kanboard import Kanboard

    kb = Kanboard("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token")
    project_id = kb.create_project(name="My project")

"""

from .kanboard import Kanboard