from cgitb import text
from operator import mod
from turtle import title
from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=150)
    text  = models.TextField()


    def __str__(self):
        return self.title