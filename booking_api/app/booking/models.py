"""
Copyright (c) Universidad Privada Boliviana (UPB) - EUBBC-Digital
MIT License - See LICENSE file in the root directory
Adriana Orellana, Angel Zenteno, Boris Pedraza, Alex Villazon, Omar Ormachea
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
import hashlib
import os
import uuid

class Booking(models.Model):

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    available = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    access_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=15, blank=True, null=True, default=None)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner', on_delete=models.CASCADE)
    reserved_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reserved_by', on_delete=models.CASCADE, blank=True, null=True, default=None)
    equipment = models.ForeignKey('Equipment', related_name='equipment_reservations', on_delete=models.CASCADE)
    timeframe = models.ForeignKey('TimeFrame', related_name='tf_reservations', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

class Equipment(models.Model):

    name = models.CharField(max_length=255, blank=False, default='')
    description = models.CharField(max_length=500, default='')
    laboratory = models.ForeignKey('Laboratory', related_name='reservations', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='equipment_owner', on_delete=models.CASCADE)
    bookings_per_user = models.IntegerField(default=3)

class TimeFrame(models.Model):

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    slot_duration = models.IntegerField()
    equipment = models.ForeignKey('Equipment', related_name='timeframes', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='timeframe_owner', on_delete=models.CASCADE)


class Laboratory(models.Model):

    name = models.CharField(max_length=255, blank=False, default='')
    instructor = models.CharField(max_length=255, blank=False, default='')
    university = models.CharField(max_length=255, blank=False, default='')
    course = models.CharField(max_length=255, blank=False, default='')
    image = models.ImageField(upload_to='labs/', blank=True, null=True, default=None)
    description = models.CharField(max_length=1000, default='')
    url = models.CharField(max_length=255, blank=True, null=True, default='')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    visible = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='laboratory_owner', on_delete=models.CASCADE)
    notify_owner = models.BooleanField(default=False)
    allowed_emails = models.TextField(blank=True, default='')

    def has_bookings_available(self):
      current_datetime = timezone.now()

      future_timeframes = TimeFrame.objects.filter(
          Q(enabled=True)
          & Q(equipment__in=self.reservations.all())
          & (Q(end_date__date__gt=current_datetime.date()))
          | (Q(end_date__date=current_datetime.date()) & Q(end_hour__gt=current_datetime.time()))
      )

      if future_timeframes.exists():
        available_bookings = Booking.objects.filter(
          Q(timeframe__in = future_timeframes)
          & Q(available = True)
        )
        return available_bookings.exists()

      return False

    @property
    def is_available_now(self):
        return self.has_bookings_available()

def generate_unique_filename_image(instance, filename):
    image_content = instance.image.read()
    md5_hash = hashlib.md5(image_content).hexdigest()
    _, ext = os.path.splitext(filename)
    new_filename = f"{md5_hash}{ext}"
    return os.path.join('labs_content_photos', new_filename)

def generate_unique_filename_video(instance, filename):
    video_content= instance.video.read()
    md5_hash = hashlib.md5(video_content).hexdigest()
    _, ext = os.path.splitext(filename)
    new_filename = f"{md5_hash}{ext}"
    return os.path.join('labs_content_videos', new_filename)

class UniqueFilenameStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise(Exception("name's length is greater than max_length"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            return name
        return super(UniqueFilenameStorage, self)._save(name, content)

class LaboratoryContent(models.Model):
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='contents')
    order = models.PositiveIntegerField()

    text = models.CharField(max_length=1500, blank=True, null=True)
    image = models.ImageField(
        upload_to=generate_unique_filename_image,
        storage=UniqueFilenameStorage(),
        blank=True,
        null=True
    )
    video = models.FileField(
        upload_to=generate_unique_filename_video,
        storage=UniqueFilenameStorage(),
        blank=True,
        null=True
    )
    video_link = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    is_last = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ['laboratory', 'order']
