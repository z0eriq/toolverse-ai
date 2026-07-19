# Generated manually for Launch Scale Layer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="public_username",
            field=models.SlugField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="is_public",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="profile",
            name="headline",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
