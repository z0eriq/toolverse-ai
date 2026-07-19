from django.urls import path

from tools.base import BaseToolPlugin

from .views import hash_generator_view


class HashGeneratorPlugin(BaseToolPlugin):
    tool_id = "hash-generator"

    def get_urls(self):
        return [
            path("hash-generator/", hash_generator_view, name="tool-hash-generator"),
            path(
                "hash-generator/hash/",
                hash_generator_view,
                name="tool-hash-generator-hash",
            ),
        ]


plugin = HashGeneratorPlugin()
