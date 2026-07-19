# Generated manually for Market Domination layer

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo_optimizer", "0004_gtm"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SeoAutopilotRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("running", "Running"), ("success", "Success"), ("failed", "Failed")],
                        db_index=True,
                        default="running",
                        max_length=20,
                    ),
                ),
                ("issues_created", models.PositiveIntegerField(default=0)),
                ("summary", models.TextField(blank=True, default="")),
                ("error", models.TextField(blank=True, default="")),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SeoPageIssue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(db_index=True, max_length=512)),
                (
                    "issue_type",
                    models.CharField(
                        choices=[
                            ("meta", "Meta"),
                            ("faq", "FAQ"),
                            ("internal_link", "Internal link"),
                            ("freshness", "Freshness"),
                            ("broken_link", "Broken link"),
                            ("ctr", "CTR"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                        default="medium",
                        max_length=16,
                    ),
                ),
                ("suggestion", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("applied", "Applied"), ("dismissed", "Dismissed")],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                ("evidence", models.JSONField(blank=True, default=dict)),
                (
                    "run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="issues",
                        to="seo_optimizer.seoautopilotrun",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["path", "status"], name="seo_optimiz_path_st_idx"),
                    models.Index(fields=["issue_type", "status"], name="seo_optimiz_issue_st_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="SeoApplyLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("before", models.JSONField(blank=True, default=dict)),
                ("after", models.JSONField(blank=True, default=dict)),
                ("note", models.TextField(blank=True, default="")),
                (
                    "applied_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="seo_apply_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="apply_logs",
                        to="seo_optimizer.seopageissue",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
