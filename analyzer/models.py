from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class App(models.Model):
    name = models.CharField(max_length=100)
    apk_file_path = models.FileField(upload_to='apk_files/', null=True, blank=True)
    first_screen_screenshot_path = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    second_screen_screenshot_path = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    video_recording_path = models.FileField(upload_to='videos/', null=True, blank=True)
    ui_hierarchy = models.TextField(null=True, blank=True)
    screen_changed = models.BooleanField(default=False)##
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name



class AppiumTestResult(models.Model):
    app = models.ForeignKey(App, related_name='test_results', on_delete=models.CASCADE)
    ui_hierarchy = models.TextField()
    screen_changed = models.BooleanField()
    initial_screenshot = models.ImageField(upload_to='screenshots/')
    subsequent_screenshot = models.ImageField(upload_to='screenshots/')
    log = models.TextField()  # Add this field to store logs
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test result for {self.app.name} on {self.created_at}"

