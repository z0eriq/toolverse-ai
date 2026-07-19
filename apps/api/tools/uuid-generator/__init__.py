from django.urls import path

from tools.base import BaseToolPlugin

from .views import uuid_generator_view


class UuidGeneratorPlugin(BaseToolPlugin):
    tool_id = "uuid-generator"

    def get_urls(self):
        return [
            path("uuid-generator/", uuid_generator_view, name="tool-uuid-generator"),
            path(
                "uuid-generator/generate/",
                uuid_generator_view,
                name="tool-uuid-generator-generate",
            ),
        ]


plugin = UuidGeneratorPlugin()
