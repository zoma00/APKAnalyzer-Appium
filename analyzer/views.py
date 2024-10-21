from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from analyzer.models import App ,AppiumTestResult# Ensure this is the correct import
from .forms import AppForm  # Import the form
from django.contrib import messages
from analyzer.UserCreationForm import RegistrationForm
import requests
from django.http import JsonResponse
import subprocess
from django.http import HttpResponse
from appium_tests.appium_test import run_app_evaluation
import time

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




def is_appium_running(port=4723):
    """Check if Appium server is running on the specified port."""
    try:
        output = subprocess.check_output(['lsof', '-i', f':{port}'])
        return True if output else False
    except subprocess.CalledProcessError:
        return False

@login_required
def run_appium_test(request):
    if request.method == 'POST':
        # 1. Start Appium server if it's not running
        if not is_appium_running():
            subprocess.Popen(['appium'])
            time.sleep(5)  # Give Appium some time to start

        # 2. Launch Android emulator (consider checking if it's already running)
        avd_name = 'DjangoAPKAnalyzer'
        # You might want to check if the emulator is already running before launching it again
        subprocess.Popen(['emulator', '-avd', avd_name, '-read-only'])

        # 3. Get the app instance
        app_id = request.POST.get('app_id')
        app = get_object_or_404(App, id=app_id)

        # 4. Construct the absolute APK path (assuming apk_file_path is relative)
        apk_path = os.path.join(settings.MEDIA_ROOT, app.apk_file_path.name)

        try:
            # 5. Install the APK with better error handling
            install_process = subprocess.run(['adb', 'install', '-r', apk_path], 
                                             capture_output=True, text=True, check=True)
            if install_process.returncode != 0:
                return JsonResponse({'error': f'Failed to install APK: {install_process.stderr}'})

            # 6. Run the Appium test
            run_app_evaluation(app.id)

            return JsonResponse({'status': 'Test started successfully.'})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'error': f'Error during test execution: {str(e)}'})
        except Exception as e:
            # Catch any other unexpected exceptions
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'})
    else:
        # Handle non-POST requests (optional)
        return JsonResponse({'error': 'Method not allowed.'}, status=405)



def run_appium_test(request):
    # Start Appium server if it's not running
    if not is_appium_running():
        subprocess.Popen(['appium'])  # Start Appium server in the background
        time.sleep(5)  # Wait for a few seconds to ensure Appium is ready

    # Launch Android emulator
    avd_name = 'DjangoAPKAnalyzer'  # Replace with your actual AVD name
    subprocess.Popen(['emulator', '-avd', 'DjangoAPKAnalyzer', '-read-only'])  # Ensure this AVD exists

    # Install the APK (make sure to get the path from the uploaded file)
    apk_path = request.POST.get('apk_file_path')  # Get the path from the request
    if not apk_path or not apk_path.endswith('.apk'):
        return JsonResponse({'error': 'Invalid APK path. It must end with .apk.'})

    try:
        subprocess.run(['adb', 'install', apk_path], check=True)
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': f'Failed to install APK: {str(e)}'})

    # Run the Appium test script
    result = subprocess.run(['python', 'path/to/your/appium_test.py'], capture_output=True, text=True)

    return JsonResponse({'output': result.stdout, 'error': result.stderr})



@login_required
def app_detail(request, app_id):
    app = get_object_or_404(App, id=app_id)
    test_results = AppiumTestResult.objects.filter(app=app)  # Fetch related test results
    return render(request, 'analyzer/app_detail.html', {'app': app, 'test_results': test_results})

def app_detail(request, app_id):
    app_instance = get_object_or_404(App, id=app_id, uploaded_by=request.user)
    test_results = app_instance.test_results.all()
    return render(request, 'analyzer/app_detail.html', {'app': app_instance, 'test_results': test_results})

@login_required
def run_app_evaluation(app_id):
    try:
        app = App.objects.get(id=app_id)
        evaluator = AppEvaluator(app.apk_file_path)  # Use the apk_path from the app object
        evaluator.run_evaluation()
    except App.DoesNotExist:
        print(f"App with ID '{app_id}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        evaluator.cleanup()



def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    log_output = "Test started...\n"  # Initialize log output

    try:
        driver = setup_appium("DjangoAPKAnalyzer")
        log_output += "Performing actions...\n"

        # Perform your test actions here
        # Log each significant step
        # Example: log_output += "Action performed: [description]\n"

        log_output += "Test completed successfully."

        # Save results to the database
        save_test_result(app, first_screenshot_path, subsequent_screenshot_path, log_output)

    except Exception as e:
        log_output += f"An error occurred: {e}"
    finally:
        if driver:
            driver.quit()

def save_test_result(app, initial_screenshot_path, subsequent_screenshot_path, log_output):
    with open(initial_screenshot_path, 'rb') as initial_file:
        initial_screenshot = File(initial_file)

        with open(subsequent_screenshot_path, 'rb') as subsequent_file:
            subsequent_screenshot = File(subsequent_file)

            result = AppiumTestResult(
                app=app,
                initial_screenshot=initial_screenshot,
                subsequent_screenshot=subsequent_screenshot,
                log=log_output,  # Ensure this line is present
                created_at=timezone.now()
            )
            result.save()

    # Log output can be printed or logged here if needed
    print(f"Log Output: {log_output}")







