# Generated manually for Market Domination layer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmatic_seo", "0002_global_launch_engine"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programmaticpage",
            name="page_type",
            field=models.CharField(
                choices=[
                    ("best_of", "Best of"),
                    ("keyword", "Keyword"),
                    ("audience", "Audience"),
                    ("category_hub", "Category hub"),
                    ("authority", "Authority"),
                    ("use_case", "Use case"),
                    ("industry", "Industry"),
                    ("comparison", "Comparison"),
                ],
                db_index=True,
                default="keyword",
                max_length=32,
            ),
        ),
    ]
