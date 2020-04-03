# Generated by Django 2.1.7 on 2020-04-02 19:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_auto_20200401_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='seq2seqannotation',
            name='sentence',
            field=models.CharField(default='none', max_length=500),
        ),
        migrations.AlterUniqueTogether(
            name='seq2seqannotation',
            unique_together={('document', 'user', 'text', 'sentence')},
        ),
    ]
