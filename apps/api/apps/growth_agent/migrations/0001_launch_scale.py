# Generated manually for Launch Scale Layer

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GrowthInsight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("traffic", "Traffic"),
                            ("seo", "SEO"),
                            ("tools", "Tools"),
                            ("revenue", "Revenue"),
                            ("content", "Content"),
                        ],
                        db_index=True,
                        max_length=32,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("rationale", models.TextField(blank=True, default="")),
                ("priority", models.IntegerField(db_index=True, default=50)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("accepted", "Accepted"),
                            ("dismissed", "Dismissed"),
                        ],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                ("meta", models.JSONField(blank=True, default=dict)),
                ("source_snapshot", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-priority", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="GrowthAgentRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("running", "Running"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="running",
                        max_length=20,
                    ),
                ),
                ("summary", models.TextField(blank=True, default="")),
                ("insights_created", models.PositiveIntegerField(default=0)),
                ("error", models.TextField(blank=True, default="")),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="growthinsight",
            index=models.Index(fields=["status", "-priority"], name="growth_agen_status_prio_idx"),
        ),
        migrations.AddIndex(
            model_name="growthinsight",
            index=models.Index(fields=["category", "status"], name="growth_agen_cat_status_idx"),
        ),
    ]
