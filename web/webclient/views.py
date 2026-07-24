"""
Webclient views - 自定义 webclient 页面
"""

from django.shortcuts import render


def webclient_view(request):
    """渲染自定义 webclient 页面"""
    return render(request, "webclient/webclient.html")