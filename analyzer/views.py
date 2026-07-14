import os
import subprocess
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from analyzer.models import App
from analyzer.UserCreationForm import RegistrationForm
from appium_tests.appium_test import run_app_evaluation
from .forms import AppForm


@login_required
def index(request):
    apps = App.objects.filter(uploaded_by=request.user)
    return render(request, 'analyzer/index.html', {'apps': apps})


def app_list(request):
    apps = App.objects.all()
    return render(request, 'analyzer/app_list.html', {'apps': apps})


@login_required
def create_item(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.uploaded_by = request.user
            item.save()
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
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'analyzer/register.html', {'form': form})


@login_required
def delete_item(request, app_id):
    # Owner-scoped lookup: users can only delete their own apps
    app = get_object_or_404(App, id=app_id, uploaded_by=request.user)
    if request.method == 'POST':
        app.delete()
        return redirect('app_list')
    return render(request, 'analyzer/delete_item.html', {'app': app})


@login_required
def edit_item(request, app_id):
    # Owner-scoped lookup: users can only edit their own apps
    app = get_object_or_404(App, id=app_id, uploaded_by=request.user)

    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            return redirect('app_list')
    else:
        form = AppForm(instance=app)

    return render(request, 'analyzer/edit_item.html', {'form': form})


@login_required
def app_detail(request, app_id):
    # Owner-scoped lookup: users can only view their own apps' results
    app_instance = get_object_or_404(App, id=app_id, uploaded_by=request.user)
    test_results = app_instance.test_results.all()
    return render(
        request,
        'analyzer/app_detail.html',
        {'app': app_instance, 'test_results': test_results},
    )


def is_appium_running(port=4723):
    """Check if the Appium server is listening on the specified port."""
    try:
        output = subprocess.check_output(['lsof', '-i', f':{port}'])
        return bool(output)
    except subprocess.CalledProcessError:
        return False


@login_required
def run_appium_test(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    # 1. Start the Appium server if it is not running
    if not is_appium_running():
        subprocess.Popen(['appium'])
        time.sleep(5)  # Give Appium some time to start

    # 2. Launch the Android emulator
    avd_name = 'DjangoAPKAnalyzer'
    subprocess.Popen(['emulator', '-avd', avd_name, '-read-only'])

    # 3. Get the app instance (owner-scoped)
    app_id = request.POST.get('app_id')
    app = get_object_or_404(App, id=app_id, uploaded_by=request.user)

    # 4. Construct the absolute APK path
    apk_path = os.path.join(settings.MEDIA_ROOT, app.apk_file_path.name)

    try:
        # 5. Install the APK
        install_process = subprocess.run(
            ['adb', 'install', '-r', apk_path],
            capture_output=True, text=True, check=True,
        )
        if install_process.returncode != 0:
            return JsonResponse(
                {'error': f'Failed to install APK: {install_process.stderr}'}
            )

        # 6. Run the Appium evaluation (screenshots + result persisted)
        run_app_evaluation(app.id)

        return JsonResponse({'status': 'Test started successfully.'})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': f'Error during test execution: {e}'})
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {e}'})
