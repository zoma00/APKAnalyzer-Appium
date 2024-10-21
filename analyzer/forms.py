# analyzer/forms.py
from django import forms
from .models import App  # Ensure this is the correct import

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'apk_file_path', 'first_screen_screenshot_path', 'second_screen_screenshot_path', 'video_recording_path']