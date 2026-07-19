# Generated manually for Launch Scale Layer

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tool_factory", "0001_traffic_revenue_engine"),
    ]

    operations = [
        migrations.CreateModel(
            name="CreatorProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("display_name", models.CharField(blank=True, default="", max_length=120)),
                ("bio", models.TextField(blank=True, default="")),
                ("payout_ready", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["display_name", "id"]},
        ),
        migrations.CreateModel(
            name="CreatorSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[("tool", "Tool"), ("template", "Template")],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        db_index=True,
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("reviewer_notes", models.TextField(blank=True, default="")),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="creator_hub.creatorprofile",
                    ),
                ),
                (
                    "tool_spec",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="creator_submissions",
                        to="tool_factory.toolspec",
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="CreatorUsageStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tool_slug", models.SlugField(blank=True, default="", max_length=128)),
                ("period", models.CharField(db_index=True, max_length=32)),
                ("runs", models.PositiveIntegerField(default=0)),
                ("unique_users", models.PositiveIntegerField(default=0)),
                (
                    "submission",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_stats",
                        to="creator_hub.creatorsubmission",
                    ),
                ),
            ],
            options={"ordering": ["-period"]},
        ),
        migrations.CreateModel(
            name="CreatorRevenueShareStub",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period", models.CharField(db_index=True, max_length=32)),
                ("amount_cents", models.IntegerField(default=0)),
                ("share_bps", models.PositiveIntegerField(default=7000)),
                (
                    "status",
                    models.CharField(
                        choices=[("accrued", "Accrued"), ("paid", "Paid")],
                        db_index=True,
                        default="accrued",
                        max_length=20,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revenue_shares",
                        to="creator_hub.creatorprofile",
                    ),
                ),
            ],
            options={"ordering": ["-period"]},
        ),
        migrations.AlterUniqueTogether(
            name="creatorrevenuesharestub",
            unique_together={("creator", "period")},
        ),
        migrations.AddIndex(
            model_name="creatorsubmission",
            index=models.Index(fields=["status", "-updated_at"], name="creator_hub_status_upd_idx"),
        ),
        migrations.AddIndex(
            model_name="creatorsubmission",
            index=models.Index(fields=["type", "status"], name="creator_hub_type_status_idx"),
        ),
        migrations.AddIndex(
            model_name="creatorusagestat",
            index=models.Index(fields=["tool_slug", "period"], name="creator_hub_slug_period_idx"),
        ),
    ]
