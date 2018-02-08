"""
For more information on this file, see
http://channels.readthedocs.io/en/1.x/installation.html
"""

import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.settings")
channel_layer = get_channel_layer()
