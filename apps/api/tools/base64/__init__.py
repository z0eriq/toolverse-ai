from django.urls import path

from tools.base import BaseToolPlugin

from .views import base64_view


class Base64Plugin(BaseToolPlugin):
    tool_id = "base64"

    def get_urls(self):
        return [
            path("base64/", base64_view, name="tool-base64"),
            path("base64/encode/", base64_view, name="tool-base64-encode"),
        ]


plugin = Base64Plugin()
