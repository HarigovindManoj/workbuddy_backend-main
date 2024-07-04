from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    path('ws/ticket/<project_id>/', consumers.TicketConsumer.as_asgi()),
]
