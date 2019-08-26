# Generated by Django 2.2.4 on 2019-08-26 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('assignee', models.IntegerField()),
                ('due_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
