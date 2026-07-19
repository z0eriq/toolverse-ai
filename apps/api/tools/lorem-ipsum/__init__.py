from django.urls import path

from tools.base import BaseToolPlugin

from .views import lorem_ipsum_view


class LoremIpsumPlugin(BaseToolPlugin):
    tool_id = "lorem-ipsum"

    def get_urls(self):
        return [
            path("lorem-ipsum/", lorem_ipsum_view, name="tool-lorem-ipsum"),
            path(
                "lorem-ipsum/generate/",
                lorem_ipsum_view,
                name="tool-lorem-ipsum-generate",
            ),
        ]


plugin = LoremIpsumPlugin()
