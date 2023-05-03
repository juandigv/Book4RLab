# Generated by Django 4.1.5 on 2023-05-03 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_laboratory_course_laboratory_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='laboratory',
            name='visible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='laboratory',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='media'),
        ),
    ]
