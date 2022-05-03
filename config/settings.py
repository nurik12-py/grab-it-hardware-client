import os

RUNNING_MODE = os.getenv('env')

if RUNNING_MODE == "prod":
    from production import *
else:
    from development import *
