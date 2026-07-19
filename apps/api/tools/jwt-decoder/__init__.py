from django.urls import path

from tools.base import BaseToolPlugin

from .views import jwt_decoder_view


class JwtDecoderPlugin(BaseToolPlugin):
    tool_id = "jwt-decoder"

    def get_urls(self):
        return [
            path("jwt-decoder/", jwt_decoder_view, name="tool-jwt-decoder"),
            path("jwt-decoder/decode/", jwt_decoder_view, name="tool-jwt-decoder-decode"),
        ]


plugin = JwtDecoderPlugin()
