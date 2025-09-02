"""
WebSocket routing for listings
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/listings/(?P<listing_id>[0-9a-f-]+)/$', consumers.ListingConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]