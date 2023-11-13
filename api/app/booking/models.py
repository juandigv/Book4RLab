"""
Copyright (c) Universidad Privada Boliviana (UPB) - EUBBC-Digital
MIT License - See LICENSE file in the root directory
Adriana Orellana, Angel Zenteno, Alex Villazon, Omar Ormachea
"""

from django.db import models
from django.conf import settings
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

    def __str__(self):
        return f"{self.name} ({self.laboratory.name}) ({self.id})"

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

    def __str__(self):
        return f"{self.name} (E={self.enabled}, V={self.visible}) ({self.id})"

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
