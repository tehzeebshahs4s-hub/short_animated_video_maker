import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

# load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE, ".env"))
except Exception:
    pass

from main import app

# Phusion Passenger supports ASGI applications assigned to `application`
application = app
