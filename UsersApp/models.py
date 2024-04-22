from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=32, unique=True, null=True)
    likedProducts = models.ManyToManyField('ProductsApp.Product', related_name="likedBy")
    bucket = models.ManyToManyField('ProductsApp.Product', related_name="storedBy")
    by_phone = models.BooleanField(default=True)
    father_name = models.CharField(max_length=32, null=True)


class UserVerification(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    smsCode = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Recovery(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.IntegerField()
