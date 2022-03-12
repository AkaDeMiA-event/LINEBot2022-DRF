# Generated by Django 4.0.3 on 2022-03-12 12:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Numeron",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "number_str",
                    models.CharField(
                        max_length=4, validators=[django.core.validators.MinLengthValidator(4)]
                    ),
                ),
                ("line_id", models.CharField(max_length=300)),
            ],
        ),
    ]
