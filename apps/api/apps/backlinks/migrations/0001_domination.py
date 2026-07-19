# Generated manually for Market Domination layer

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BacklinkTarget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url", models.URLField(max_length=1024)),
                ("path", models.CharField(blank=True, db_index=True, default="", max_length=512)),
                ("title", models.CharField(blank=True, default="", max_length=255)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BacklinkCampaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
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
                ("notes", models.TextField(blank=True, default="")),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="campaigns",
                        to="backlinks.backlinktarget",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BacklinkOpportunity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_domain", models.CharField(db_index=True, max_length=255)),
                ("source_url", models.URLField(blank=True, default="", max_length=1024)),
                ("contact_email", models.EmailField(blank=True, default="", max_length=254)),
                ("priority", models.IntegerField(db_index=True, default=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("outreach", "Outreach"),
                            ("won", "Won"),
                            ("lost", "Lost"),
                            ("dismissed", "Dismissed"),
                        ],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                ("rationale", models.TextField(blank=True, default="")),
                ("meta", models.JSONField(blank=True, default=dict)),
                (
                    "campaign",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opportunities",
                        to="backlinks.backlinkcampaign",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opportunities",
                        to="backlinks.backlinktarget",
                    ),
                ),
            ],
            options={
                "ordering": ["-priority", "-created_at"],
                "indexes": [
                    models.Index(fields=["status", "-priority"], name="backlinks_o_status_p_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="BacklinkOutreachLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.CharField(default="email", max_length=64)),
                ("message", models.TextField(blank=True, default="")),
                ("outcome", models.CharField(blank=True, default="", max_length=64)),
                ("meta", models.JSONField(blank=True, default=dict)),
                (
                    "opportunity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outreach_logs",
                        to="backlinks.backlinkopportunity",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
