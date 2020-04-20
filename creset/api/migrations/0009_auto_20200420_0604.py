# Generated by Django 2.1.7 on 2020-04-20 06:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0008_auto_20200403_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='seq2seqannotation',
            name='annotation_text',
            field=models.CharField(default='none', max_length=500),
        ),
        migrations.AddField(
            model_name='seq2seqannotation',
            name='label',
            field=models.ForeignKey(default='none', on_delete=django.db.models.deletion.CASCADE, to='api.Label'),
        ),
        migrations.RemoveField(
            model_name='seq2seqannotation',
            name='sentence',
        ),
        migrations.RemoveField(
            model_name='seq2seqannotation',
            name='text',
        ),
        migrations.AlterUniqueTogether(
            name='seq2seqannotation',
            unique_together={('document', 'user', 'label', 'annotation_text')},
        ),
    ]
