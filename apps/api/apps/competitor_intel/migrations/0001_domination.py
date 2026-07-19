# Generated manually for Market Domination layer

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CompetitorDomain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("domain", models.CharField(db_index=True, max_length=255, unique=True)),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("notes", models.TextField(blank=True, default="")),
            ],
            options={"ordering": ["domain"]},
        ),
        migrations.CreateModel(
            name="CompetitorKeyword",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("keyword", models.CharField(db_index=True, max_length=255)),
                ("position", models.FloatField(default=0.0)),
                ("search_volume", models.PositiveIntegerField(default=0)),
                ("our_has_coverage", models.BooleanField(db_index=True, default=False)),
                (
                    "competitor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="keywords",
                        to="competitor_intel.competitordomain",
                    ),
                ),
            ],
            options={
                "ordering": ["-search_volume", "keyword"],
                "unique_together": {("competitor", "keyword")},
            },
        ),
        migrations.CreateModel(
            name="CompetitorOpportunity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("keyword", models.CharField(db_index=True, max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("rationale", models.TextField(blank=True, default="")),
                ("gap_score", models.FloatField(db_index=True, default=0.0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("queued", "Queued"),
                            ("done", "Done"),
                            ("dismissed", "Dismissed"),
                        ],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                ("evidence", models.JSONField(blank=True, default=dict)),
                (
                    "competitor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opportunities",
                        to="competitor_intel.competitordomain",
                    ),
                ),
            ],
            options={
                "ordering": ["-gap_score", "-created_at"],
                "unique_together": {("competitor", "keyword")},
                "indexes": [
                    models.Index(fields=["status", "-gap_score"], name="competitor__status_g_idx"),
                ],
            },
        ),
    ]
