# Generated manually for Market Domination layer

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("growth_agent", "0003_gtm"),
    ]

    operations = [
        migrations.CreateModel(
            name="GrowthAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("create_seo_task", "Create SEO task"),
                            ("queue_tool_spec", "Queue tool spec"),
                            ("start_autopilot", "Start autopilot"),
                            ("create_content_draft", "Create content draft"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("proposed", "Proposed"),
                            ("approved", "Approved"),
                            ("executed", "Executed"),
                            ("rejected", "Rejected"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="proposed",
                        max_length=20,
                    ),
                ),
                ("result_ref", models.JSONField(blank=True, default=dict)),
                ("error", models.TextField(blank=True, default="")),
                (
                    "task",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="actions",
                        to="growth_agent.growthtask",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status", "action_type"], name="growth_agen_status_act_idx"),
                    models.Index(fields=["action_type", "-created_at"], name="growth_agen_action_cr_idx"),
                ],
            },
        ),
    ]
