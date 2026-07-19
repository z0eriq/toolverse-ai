# Initial Campaign Manager models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MarketingCampaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("key", models.SlugField(max_length=128, unique=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "channel",
                    models.CharField(
                        choices=[
                            ("search", "Search"),
                            ("social", "Social"),
                            ("email", "Email"),
                            ("affiliate", "Affiliate"),
                            ("partner", "Partner"),
                            ("other", "Other"),
                        ],
                        db_index=True,
                        default="other",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("paused", "Paused"),
                            ("completed", "Completed"),
                        ],
                        db_index=True,
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("budget_cents", models.PositiveIntegerField(default=0)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("meta", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="CampaignResultDaily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(db_index=True)),
                ("impressions", models.PositiveIntegerField(default=0)),
                ("clicks", models.PositiveIntegerField(default=0)),
                ("conversions", models.PositiveIntegerField(default=0)),
                ("revenue_cents", models.IntegerField(default=0)),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_results",
                        to="campaigns.marketingcampaign",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("campaign", "date")},
            },
        ),
        migrations.AddIndex(
            model_name="marketingcampaign",
            index=models.Index(fields=["status", "channel"], name="campaigns_m_status_idx"),
        ),
        migrations.AddIndex(
            model_name="campaignresultdaily",
            index=models.Index(fields=["date", "campaign"], name="campaigns_c_date_ca_idx"),
        ),
    ]
