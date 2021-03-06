# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-17 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='q_type',
            field=models.CharField(choices=[('combo', 'Combo Box'), ('check', 'Check Boxes'), ('drugs', 'Drugs'), ('text', 'Text Field'), ('int', 'Integer Field'), ('bool', 'Yes or No')], max_length=5),
        ),
    ]
