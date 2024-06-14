# Generated by Django 5.0.6 on 2024-06-13 17:15

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_courselecture_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courselecture',
            name='content',
            field=models.FileField(max_length=500, upload_to=core.models.get_course_lecture_file_path),
        ),
    ]
