import os

from channels.auth import AuthMiddlewareStack
from .middleware import TokenAuthMiddleware

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workbuddy_backend.settings')
django_asgi_app = get_asgi_application()

import core.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(URLRouter(core.routing.websocket_urlpatterns))
        ),
    }
)
