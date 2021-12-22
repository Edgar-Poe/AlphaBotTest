# Generated by Django 4.0 on 2021-12-20 00:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatInUse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('stage', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MessageInChatInUse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField()),
                ('from_chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.chatinuse')),
            ],
        ),
    ]
