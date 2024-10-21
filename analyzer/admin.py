from django.contrib import admin
from .models import App, AppiumTestResult  # Import the App model

@admin.register(App)  # Register the App model
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_by')  # Customize the admin display
    search_fields = ('name',)  # Add search functionality

# Alternatively, you can use the following if you prefer a simpler registration:
# admin.site.register(App)
@admin.register(AppiumTestResult)
class AppiumTestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'app', 'screen_changed')
    # Add any other fields you want to display