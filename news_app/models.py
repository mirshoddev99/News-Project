from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


# from .managers import PublishedManager

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=News.Status.publish.value)


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class News(models.Model):
    class Status(models.TextChoices):
        draft = "DF", "Draft"
        publish = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    image = models.ImageField(upload_to='news/images', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news')
    published_time = models.DateTimeField(default=timezone.now)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.draft)
    objects = models.Manager()  # default
    published = PublishedManager()  # custom manager

    class Meta:
        ordering = ['-published_time']

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    body = models.TextField()

    def __str__(self):
        return self.name


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_time']

    def __str__(self):
        return f"commented by {self.user.username}"
