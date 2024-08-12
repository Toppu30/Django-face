from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Member(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    details = models.TextField(blank=True, null=True)
    face_image = models.ImageField(upload_to='face_images/', blank=True, null=True)
    face_encoding = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CustomerVisit(models.Model):
    date = models.DateField(auto_now_add=True)  # วันที่ลูกค้าเข้ามา
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)  # ถ้าเป็นสมาชิกจะเก็บข้อมูลสมาชิก
    is_member = models.BooleanField(default=False)  # บอกว่าลูกค้าเป็นสมาชิกหรือไม่

    def __str__(self):
        return f"{self.date} - {'Member' if self.is_member else 'Non-member'}"