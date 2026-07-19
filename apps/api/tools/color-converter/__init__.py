from django.urls import path

from tools.base import BaseToolPlugin

from .views import color_converter_view


class ColorConverterPlugin(BaseToolPlugin):
    tool_id = "color-converter"

    def get_urls(self):
        return [
            path("color-converter/", color_converter_view, name="tool-color-converter"),
            path(
                "color-converter/convert/",
                color_converter_view,
                name="tool-color-converter-convert",
            ),
        ]


plugin = ColorConverterPlugin()
