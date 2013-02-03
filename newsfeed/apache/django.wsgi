import os
import sys

path = '/home/justin/demo'
if path not in sys.path:
        sys.path.append(path)
sys.path.append('/home/justin/demo/newsfeed')

os.environ['DJANGO_SETTINGS_MODULE'] = 'newsfeed.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
