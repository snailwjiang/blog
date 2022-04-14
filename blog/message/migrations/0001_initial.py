# Generated by Django 2.2.12 on 2022-04-13 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('topic', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=50, verbose_name='留言')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('parent_message', models.IntegerField(default=0)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topic.Topic')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserProfile')),
            ],
        ),
    ]
