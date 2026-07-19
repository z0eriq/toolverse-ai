from django.contrib import admin

from apps.competitor_intel.models import CompetitorDomain, CompetitorKeyword, CompetitorOpportunity


@admin.register(CompetitorDomain)
class CompetitorDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("domain", "name")


@admin.register(CompetitorKeyword)
class CompetitorKeywordAdmin(admin.ModelAdmin):
    list_display = ("keyword", "competitor", "position", "search_volume", "our_has_coverage")
    list_filter = ("our_has_coverage",)
    search_fields = ("keyword",)


@admin.register(CompetitorOpportunity)
class CompetitorOpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "keyword", "gap_score", "status", "competitor")
    list_filter = ("status",)
    search_fields = ("title", "keyword")
