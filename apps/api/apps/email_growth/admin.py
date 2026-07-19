from django.contrib import admin

from apps.email_growth.models import EmailCampaign, EmailSendLog, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "locale", "is_active", "source", "created_at")
    list_filter = ("is_active", "locale")
    search_fields = ("email",)


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("slug", "subject", "status", "sent_at", "created_at")
    list_filter = ("status",)
    search_fields = ("slug", "subject")


@admin.register(EmailSendLog)
class EmailSendLogAdmin(admin.ModelAdmin):
    list_display = ("email", "campaign", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("email",)
