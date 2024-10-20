# analyzer/forms.py
from django import forms
from .models import App  # Ensure this is the correct import

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'apk_file_path']  # Adjust field names as needed
