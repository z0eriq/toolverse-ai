# Generated manually for Launch Scale Layer

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(max_length=128, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("steps", models.JSONField(blank=True, default=list)),
                ("category", models.CharField(blank=True, db_index=True, default="general", max_length=64)),
                ("is_public", models.BooleanField(db_index=True, default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Workflow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=160)),
                ("steps", models.JSONField(blank=True, default=list)),
                (
                    "visibility",
                    models.CharField(
                        choices=[("private", "Private"), ("unlisted", "Unlisted"), ("public", "Public")],
                        db_index=True,
                        default="private",
                        max_length=20,
                    ),
                ),
                ("share_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workflows",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="WorkflowRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="queued",
                        max_length=20,
                    ),
                ),
                ("input", models.JSONField(blank=True, default=dict)),
                ("output", models.JSONField(blank=True, default=dict)),
                ("error", models.TextField(blank=True, default="")),
                ("duration_ms", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_runs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="runs",
                        to="workflows.workflow",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="WorkflowUsageDaily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(db_index=True)),
                ("runs", models.PositiveIntegerField(default=0)),
                (
                    "workflow",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_daily",
                        to="workflows.workflow",
                    ),
                ),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.AlterUniqueTogether(
            name="workflow",
            unique_together={("owner", "slug")},
        ),
        migrations.AlterUniqueTogether(
            name="workflowusagedaily",
            unique_together={("workflow", "date")},
        ),
        migrations.AddIndex(
            model_name="workflow",
            index=models.Index(fields=["visibility", "-updated_at"], name="workflows_w_vis_upd_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["workflow", "-created_at"], name="workflows_w_wf_created_idx"),
        ),
    ]
