# Generated by Django 5.0.6 on 2024-06-21 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_course_options_alter_courselecture_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courselecture',
            name='order',
            field=models.IntegerField(),
        ),
    ]