# SalesLead launch attribution fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0003_gtm"),
    ]

    operations = [
        migrations.AddField(
            model_name="saleslead",
            name="company_size",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="saleslead",
            name="utm_source",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="saleslead",
            name="utm_medium",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="saleslead",
            name="utm_campaign",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="saleslead",
            name="campaign_key",
            field=models.CharField(blank=True, db_index=True, default="", max_length=128),
        ),
    ]
