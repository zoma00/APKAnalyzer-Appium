from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class App(models.Model):
    name = models.CharField(max_length=100)
    apk_file_path = models.FileField(upload_to='apk_files/', null=True, blank=True)  # Allow null and blank
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



