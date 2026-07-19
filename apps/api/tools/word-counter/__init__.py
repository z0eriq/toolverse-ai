from django.urls import path

from tools.base import BaseToolPlugin

from .views import word_counter_view


class WordCounterPlugin(BaseToolPlugin):
    tool_id = "word-counter"

    def get_urls(self):
        return [
            path("word-counter/", word_counter_view, name="tool-word-counter"),
            path("word-counter/count/", word_counter_view, name="tool-word-counter-count"),
        ]


plugin = WordCounterPlugin()
