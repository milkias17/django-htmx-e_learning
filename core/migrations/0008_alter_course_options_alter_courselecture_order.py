# Generated by Django 5.0.6 on 2024-06-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_courselecture_content'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-updated_at']},
        ),
        migrations.AlterField(
            model_name='courselecture',
            name='order',
            field=models.IntegerField(unique=True),
        ),
    ]