from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from analyzer.models import App  # Ensure this is the correct import
from .forms import AppForm  # Import the form
from django.contrib import messages
from analyzer.UserCreationForm import RegistrationForm
import requests

@login_required  # Ensure the user is logged in to access this view
def index(request):
    apps = App.objects.filter(uploaded_by=request.user)  # Fetch user's apps
    return render(request, 'analyzer/index.html', {'apps': apps})

def app_list(request):
    apps = App.objects.all()  # Fetch all apps
    return render(request, 'analyzer/app_list.html', {'apps': apps})

@login_required
def create_item(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)  # Don't save to the database yet
            item.uploaded_by = request.user  # Set the user who uploaded
            item.save()  # Now save it
            return redirect('app_list')
    else:
        form = AppForm()
    return render(request, 'analyzer/create_item.html', {'form': form})



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # Redirect to login page after registration
    else:
        form = RegistrationForm()
    return render(request, 'analyzer/register.html', {'form': form})





def delete_item(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(App, id=app_id)
        app.delete()
        return redirect('app_list')  # Redirect to the app list after deletion




@login_required
def edit_item(request, app_id):
    app = get_object_or_404(App, id=app_id)
    
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES, instance=app)  # Bind the form to the existing app instance
        if form.is_valid():
            form.save()  # Save the updated app
            return redirect('app_list')  # Redirect to the app list after editing
    else:
        form = AppForm(instance=app)  # Populate the form with the app data

    return render(request, 'analyzer/edit_item.html', {'form': form})
