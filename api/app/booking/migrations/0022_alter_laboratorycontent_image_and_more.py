# Generated by Django 4.1.5 on 2023-12-12 20:40

import booking.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0021_laboratorycontent_is_last'),
    ]

    operations = [
        migrations.AlterField(
            model_name='laboratorycontent',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=booking.models.UniqueFilenameStorage(), upload_to=booking.models.generate_unique_filename_image),
        ),
        migrations.AlterField(
            model_name='laboratorycontent',
            name='video',
            field=models.FileField(blank=True, null=True, storage=booking.models.UniqueFilenameStorage(), upload_to=booking.models.generate_unique_filename_video),
        ),
    ]
