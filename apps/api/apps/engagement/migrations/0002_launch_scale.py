# Generated manually for Launch Scale Layer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engagement", "0001_growth_engine"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="is_public",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="collection",
            name="public_slug",
            field=models.SlugField(blank=True, max_length=160, null=True, unique=True),
        ),
    ]
