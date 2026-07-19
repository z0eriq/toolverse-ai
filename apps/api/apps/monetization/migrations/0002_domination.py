# Generated manually for Market Domination layer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monetization", "0001_traffic_revenue_engine"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdPerformanceDaily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField(db_index=True)),
                ("placement_key", models.CharField(db_index=True, max_length=32)),
                ("impressions", models.PositiveIntegerField(default=0)),
                ("clicks", models.PositiveIntegerField(default=0)),
                ("revenue_cents", models.IntegerField(default=0)),
                ("ctr", models.FloatField(default=0.0)),
                ("rpm", models.FloatField(default=0.0)),
            ],
            options={
                "ordering": ["-date", "placement_key"],
                "unique_together": {("date", "placement_key")},
                "indexes": [
                    models.Index(fields=["placement_key", "-date"], name="monetizatio_placeme_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AdOptimizationRec",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("placement_key", models.CharField(blank=True, db_index=True, default="", max_length=32)),
                ("title", models.CharField(max_length=255)),
                ("rationale", models.TextField(blank=True, default="")),
                ("priority", models.IntegerField(db_index=True, default=50)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("accepted", "Accepted"), ("dismissed", "Dismissed")],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                ("evidence", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-priority", "-created_at"],
                "indexes": [
                    models.Index(fields=["status", "-priority"], name="monetizatio_status_p_idx"),
                ],
            },
        ),
    ]
