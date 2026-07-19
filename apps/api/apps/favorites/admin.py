from django.contrib import admin

from apps.favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "tool", "created_at")
    search_fields = ("user__email", "tool__tool_id")
