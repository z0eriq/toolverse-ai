from django.urls import path

from tools.base import BaseToolPlugin

from .views import url_encoder_view


class UrlEncoderPlugin(BaseToolPlugin):
    tool_id = "url-encoder"

    def get_urls(self):
        return [
            path("url-encoder/", url_encoder_view, name="tool-url-encoder"),
            path("url-encoder/encode/", url_encoder_view, name="tool-url-encoder-encode"),
        ]


plugin = UrlEncoderPlugin()
