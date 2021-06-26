# Generated by Django 3.2.4 on 2021-06-26 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.PositiveSmallIntegerField(help_text='The session number on the BBC News Review website.', primary_key=True, serialize=False)),
                ('headline', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('date', models.DateField()),
                ('raw_content', models.TextField()),
                ('video', models.CharField(help_text='The videoId from Youtube.', max_length=11, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('term', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('meaning', models.CharField(max_length=128)),
                ('examples', models.TextField(blank=True, max_length=510)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.episode')),
            ],
        ),
    ]
