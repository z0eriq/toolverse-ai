from django.urls import path

from tools.base import BaseToolPlugin

from .views import markdown_preview_view


class MarkdownPreviewPlugin(BaseToolPlugin):
    tool_id = "markdown-preview"

    def get_urls(self):
        return [
            path("markdown-preview/", markdown_preview_view, name="tool-markdown-preview"),
            path(
                "markdown-preview/render/",
                markdown_preview_view,
                name="tool-markdown-preview-render",
            ),
        ]


plugin = MarkdownPreviewPlugin()
