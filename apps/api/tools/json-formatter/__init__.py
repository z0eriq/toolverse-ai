from django.urls import path

from tools.base import BaseToolPlugin

from .views import json_formatter_view


class JsonFormatterPlugin(BaseToolPlugin):
    tool_id = "json-formatter"

    def get_urls(self):
        return [
            path("json-formatter/", json_formatter_view, name="tool-json-formatter"),
            path("json-formatter/format/", json_formatter_view, name="tool-json-formatter-format"),
        ]


plugin = JsonFormatterPlugin()
