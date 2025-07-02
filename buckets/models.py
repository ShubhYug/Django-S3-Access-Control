# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Bucket(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=50)
    prefix = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class BucketPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_upload = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.bucket.name}"
