from django.db import models
from django.conf import settings
import uuid

class Booking(models.Model):

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    available = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    access_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=15, blank=True, null=True, default=None)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner', on_delete=models.CASCADE)
    reserved_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reserved_by', on_delete=models.CASCADE, blank=True, null=True, default=None)
    kit = models.ForeignKey('Kit', related_name='reservations', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['start_date']


class Kit(models.Model):

    name = models.CharField(max_length=255, blank=False, default='')
    description = models.CharField(max_length=255, default='')
    laboratory = models.ForeignKey('Laboratory', related_name='reservations', on_delete=models.CASCADE)
    

class Laboratory(models.Model):

    name = models.CharField(max_length=255, blank=False, default='')
    description = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=255, blank=True, null=True, default='')
