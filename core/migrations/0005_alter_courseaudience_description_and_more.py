# Generated by Django 5.0.6 on 2024-06-11 11:20

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_course_price'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseaudience',
            name='description',
            field=models.TextField(verbose_name='Who is this course for?'),
        ),
        migrations.AlterField(
            model_name='courserequirement',
            name='description',
            field=models.TextField(verbose_name='Requirement'),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.FloatField()),
                ('currency', models.CharField(default='ETB', max_length=25)),
                ('payment_title', models.CharField(default='Payment', max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Created', 'CREATED'), ('Pending', 'PENDING'), ('Success', 'SUCCESS'), ('Failed', 'FAILED')], default='Created', max_length=50)),
                ('response_dump', models.JSONField(blank=True, default=dict)),
                ('checkout_url', models.URLField(blank=True, null=True)),
                ('courses', models.ManyToManyField(to='core.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]