# Generated by Django 5.0.6 on 2024-06-13 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_courseaudience_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courselecture',
            name='order',
            field=models.IntegerField(default=0, unique=True),
        ),
    ]
