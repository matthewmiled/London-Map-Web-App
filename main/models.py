from django.db import models
from django import forms
from django.contrib.auth.models import User
import pandas as pd


class Area(models.Model):
    area_name = models.CharField(max_length=255)
    borough_name = models.CharField(max_length=255)

    def __str__(self):
        return self.area_name

'''

class Visitor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.ManyToManyField(Area, blank=True)

    def __str__(self):
        return str(self.user)

'''


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class LoggedVisitInstance(models.Model):
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, blank=True, on_delete=models.CASCADE)
    comment = models.TextField()
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return f"Visit to {self.area} by {self.user}"


class Borough(models.Model):
    borough_name = models.CharField(max_length=255)

