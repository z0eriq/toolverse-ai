# Generated manually for Launch Scale Layer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo_optimizer", "0001_traffic_revenue_engine"),
    ]

    operations = [
        migrations.CreateModel(
            name="SeoHealthScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("path", models.CharField(db_index=True, max_length=512, unique=True)),
                ("metadata", models.FloatField(default=0.0)),
                ("schema", models.FloatField(default=0.0)),
                ("internal_links", models.FloatField(default=0.0)),
                ("content_quality", models.FloatField(default=0.0)),
                ("keyword_coverage", models.FloatField(default=0.0)),
                ("performance", models.FloatField(default=70.0)),
                ("overall", models.FloatField(db_index=True, default=0.0)),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("analyzed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["-overall", "path"],
                "indexes": [
                    models.Index(fields=["-overall"], name="seo_optimiz_overall_idx"),
                    models.Index(fields=["-analyzed_at"], name="seo_optimiz_analyze_idx"),
                ],
            },
        ),
    ]
