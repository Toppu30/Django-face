# members/models.py

from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    details = models.TextField(blank=True, null=True)
    face_image = models.ImageField(upload_to='face_images/', blank=True, null=True)
    face_encoding = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
