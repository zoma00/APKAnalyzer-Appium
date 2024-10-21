import os
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions  as EC
from analyzer.models import App 
import logging
import os
from datetime import datetime
import subprocess
from zipfile import ZipFile
from xml.etree import ElementTree
from django.conf import settings

   class AppEvaluator:
    def __init__(self, apk_path):
        # Assuming your Appium test code is located within the Django project's root directory
        self.apk_path = "media/apk_files/app-release-signed.apk" 
        self.driver = None
        self.video_filename = "test_video.avi"
        self.video_writer = None
           # Construct the absolute path using Django's settings
        self.apk_path = os.path.join(settings.BASE_DIR, apk_path) 

    def setup_appium(self):
        # 1. Fetch the app object using its index number (replace 0 with the desired index)
        try:
            app = App.objects.all()[0]  # Get the first app in the database
        except IndexError:
            print("No apps found in the database.")
            return  # Or handle the error appropriately

        self.apk_path = app.apk_file_path  # Update the apk_path attribute

        # 2. Extract main_activity from AndroidManifest.xml
        main_activity = self.get_main_activity_from_apk()

        # 3. Install the APK if not already installed
        if not is_app_installed(app.package_name): 
            print("Installing APK...")
            subprocess.call(['adb', 'install', '-r', self.apk_path])

        # 4. Verify installation
        if not is_app_installed(app.package_name):
            print("APK installation failed. Please check the path and try again.")
            return

        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'appPackage': app.package_name,
            'appActivity': main_activity,  # Use the extracted main_activity
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True, 
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(50)  


    def get_main_activity_from_apk(self):
        with ZipFile(self.apk_path, 'r') as zip_ref:
            try:
                manifest_data = zip_ref.read('AndroidManifest.xml')
                manifest_tree = ElementTree.fromstring(manifest_data)
                application_node = manifest_tree.find('application')
                
                for activity_node in application_node.findall('activity'):
                    intent_filter_node = activity_node.find('intent-filter')
                    if intent_filter_node is not None:
                        for action_node in intent_filter_node.findall('action'):
                            if action_node.get('android:name') == 'android.intent.action.MAIN':
                                for category_node in intent_filter_node.findall('category'):
                                    if category_node.get('android:name') == 'android.intent.category.LAUNCHER':
                                        return activity_node.get('android:name')
            except Exception as e:
                logging.error(f"Error extracting main activity from APK: {e}")
                return None  # Or handle the error appropriately

def run_app_evaluation(app_index):
    try:
        app = App.objects.all()[app_index]  # Get the app by its index
        evaluator = AppEvaluator(app.apk_file_path) 
        evaluator.run_evaluation()
    except IndexError:
        print(f"App with index '{app_index}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        evaluator.cleanup()

if __name__ == "__main__":
    run_app_evaluation(26)  # Pass the index of your app here (0 for the first app)