# Generated by Django 3.1.1 on 2020-12-01 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20201130_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='subject',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
