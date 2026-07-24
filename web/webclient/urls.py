"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls starting with `webclient/`
(the `webclient/` part should not be included again here).

"""

from django.urls import path

from evennia.web.webclient.urls import urlpatterns as evennia_webclient_urlpatterns
from .views import webclient_view

# 自定义 webclient 页面，放在 Evennia 默认路由之前以覆盖
urlpatterns = [
    path("", webclient_view, name="webclient"),
]

# read by Django
urlpatterns = urlpatterns + evennia_webclient_urlpatterns