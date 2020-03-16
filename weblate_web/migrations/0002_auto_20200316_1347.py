# Generated by Django 3.0.4 on 2020-03-16 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weblate_web", "0001_squashed_0030_service_note"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="components",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="report", name="languages", field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="report", name="projects", field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="report", name="site_url", field=models.URLField(default=""),
        ),
        migrations.AlterField(
            model_name="report", name="users", field=models.IntegerField(default=0),
        ),
    ]
