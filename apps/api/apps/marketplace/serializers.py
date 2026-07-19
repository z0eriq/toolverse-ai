from rest_framework import serializers

from apps.marketplace.models import ApiInvoiceStub, ApiKey, DeveloperOrganization, SalesLead


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = (
            "id",
            "name",
            "key_prefix",
            "scopes",
            "rate_limit_per_minute",
            "monthly_quota",
            "usage_this_month",
            "revoked_at",
            "last_used_at",
            "created_at",
        )
        read_only_fields = fields


class ApiKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    scopes = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        default=list,
    )
    rate_limit_per_minute = serializers.IntegerField(required=False, min_value=1, default=60)
    monthly_quota = serializers.IntegerField(required=False, min_value=1, default=10_000)


class DeveloperOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeveloperOrganization
        fields = ("id", "name", "owner", "plan_tier", "created_at", "updated_at")
        read_only_fields = ("id", "owner", "created_at", "updated_at")


class DeveloperOrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    plan_tier = serializers.ChoiceField(
        choices=DeveloperOrganization.PlanTier.choices,
        required=False,
        default=DeveloperOrganization.PlanTier.FREE,
    )


class ApiInvoiceStubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiInvoiceStub
        fields = (
            "id",
            "org",
            "period_start",
            "period_end",
            "amount_cents",
            "usage_units",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SalesLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesLead
        fields = (
            "id",
            "name",
            "email",
            "company",
            "company_size",
            "role",
            "message",
            "intent",
            "status",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "campaign_key",
            "meta",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")


class SalesLeadCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    company = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    company_size = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")
    role = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    message = serializers.CharField(required=False, allow_blank=True, default="")
    intent = serializers.ChoiceField(
        choices=SalesLead.Intent.choices,
        required=False,
        default=SalesLead.Intent.CONTACT,
    )
    utm_source = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    utm_medium = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    utm_campaign = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    campaign_key = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")
    meta = serializers.DictField(required=False, default=dict)
