from rest_framework import serializers

from apps.email_growth.models import EmailCampaign, NewsletterSubscriber


class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    locale = serializers.CharField(required=False, default="en", max_length=10)
    source = serializers.CharField(required=False, default="web", max_length=64)


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ("id", "email", "locale", "is_active", "source", "created_at")
        read_only_fields = fields


class EmailCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = (
            "id",
            "slug",
            "subject",
            "body_html",
            "body_text",
            "status",
            "scheduled_at",
            "sent_at",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "sent_at", "created_at", "updated_at")


class EmailCampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = ("slug", "subject", "body_html", "body_text", "status", "scheduled_at")


class SendTestSerializer(serializers.Serializer):
    email = serializers.EmailField()
