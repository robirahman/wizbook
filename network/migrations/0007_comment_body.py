# Generated by Django 3.1.1 on 2020-12-03 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_auto_20201202_0313'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='body',
            field=models.TextField(blank=True),
        ),
    ]