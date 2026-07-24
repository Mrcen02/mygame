"""
Webclient views - 自定义 webclient 页面
"""

from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def webclient_view(request):
    """渲染自定义 webclient 页面"""
    if not settings.WEBCLIENT_ENABLED:
        raise Http404

    pagevars = {"browser_sessid": request.session.session_key}
    return render(request, "webclient/webclient.html", pagevars)