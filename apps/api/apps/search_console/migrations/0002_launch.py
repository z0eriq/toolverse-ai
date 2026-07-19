# IndexedUrl for SEO indexing management

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search_console", "0001_traffic_revenue_engine"),
    ]

    operations = [
        migrations.CreateModel(
            name="IndexedUrl",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("url_path", models.CharField(db_index=True, max_length=1024, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("unknown", "Unknown"),
                            ("submitted", "Submitted"),
                            ("crawled", "Crawled"),
                            ("indexed", "Indexed"),
                            ("error", "Error"),
                        ],
                        db_index=True,
                        default="unknown",
                        max_length=20,
                    ),
                ),
                ("last_crawled_at", models.DateTimeField(blank=True, null=True)),
                ("impressions", models.PositiveIntegerField(default=0)),
                ("clicks", models.PositiveIntegerField(default=0)),
                ("position", models.FloatField(blank=True, null=True)),
                ("ranking_delta", models.FloatField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-impressions", "url_path"],
            },
        ),
        migrations.AddIndex(
            model_name="indexedurl",
            index=models.Index(fields=["status", "-impressions"], name="search_cons_status_idx"),
        ),
        migrations.AddIndex(
            model_name="indexedurl",
            index=models.Index(fields=["-clicks"], name="search_cons_clicks_idx"),
        ),
    ]
