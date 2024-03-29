# Generated by Django 3.1.1 on 2020-09-23 09:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signalpings', '0004_timersignal_corporation'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateSignal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signalpings.webhook')),
            ],
            options={
                'verbose_name': 'State Change Signal',
                'verbose_name_plural': 'State Signals',
            },
        ),
        migrations.CreateModel(
            name='CharacterSignal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_notify', models.BooleanField(default=True)),
                ('remove_notify', models.BooleanField(default=True)),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signalpings.webhook')),
            ],
            options={
                'verbose_name': 'Character Signal',
                'verbose_name_plural': 'Character Signals',
            },
        ),
    ]
