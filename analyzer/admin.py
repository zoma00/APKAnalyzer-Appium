from django.contrib import admin
from .models import App  # Import the App model

@admin.register(App)  # Register the App model
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_by')  # Customize the admin display
    search_fields = ('name',)  # Add search functionality

# Alternatively, you can use the following if you prefer a simpler registration:
# admin.site.register(App)
