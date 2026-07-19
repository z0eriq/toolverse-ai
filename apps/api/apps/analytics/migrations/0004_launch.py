# Launch attribution fields on AnalyticsEvent

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0003_analyticsdailyrollup_analyticsevent_country_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="analyticsevent",
            name="utm_source",
            field=models.CharField(blank=True, db_index=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="analyticsevent",
            name="utm_medium",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="analyticsevent",
            name="utm_campaign",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="analyticsevent",
            name="campaign_key",
            field=models.CharField(blank=True, db_index=True, default="", max_length=128),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["campaign_key", "-created_at"],
                name="analytics_a_campaig_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="analyticsevent",
            index=models.Index(
                fields=["utm_source", "-created_at"],
                name="analytics_a_utm_sou_idx",
            ),
        ),
    ]
