# Generated by Django 4.2.16 on 2025-01-07 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitations',
            name='type',
            field=models.CharField(choices=[('game', 'Game'), ('friend', 'Friend'), ('tournament', 'Tournament'), ('join', 'Join')], max_length=10),
        ),
    ]
