import os
import sys

# Adjust this path to your project folder on PythonAnywhere, e.g.:
# /home/<your_username>/MetArticles
project_home = os.path.expanduser('~/MetArticles')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from main import app as application  # WSGI entrypoint



