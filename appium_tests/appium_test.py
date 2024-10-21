import os
import time
import logging
import subprocess
from zipfile import ZipFile
from xml.etree import ElementTree
from django.conf import settings
from appium import webdriver
from analyzer.models import App
import requests

class AppEvaluator:
    def __init__(self, apk_path):
        self.apk_path = os.path.join(settings.BASE_DIR, apk_path) 
        self.driver = None

    def setup_appium(self):
        # Fetch the app object using its index number
        try:
            app = App.objects.all()[0]  # Get the first app in the database
        except IndexError:
            print("No apps found in the database.")
            return

        self.apk_path = app.apk_file_path  # Update the apk_path attribute
        package_name = 'com.example.Button'  # Set your package name here

        # Check if APK file exists
        if not os.path.exists(self.apk_path):
            print(f"APK file does not exist at {self.apk_path}")
            return

        # Install APK if not already installed
        if not self.is_app_installed(package_name):
            print("Installing APK...")
            try:
                result = subprocess.run(['adb', 'install', '-r', self.apk_path], 
                                        capture_output=True, text=True, check=True, timeout=60)
                print("APK installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"APK installation failed: {e.stderr}")
                logging.error(f"Complete ADB output: {e.stdout} {e.stderr}")
                return
            except subprocess.TimeoutExpired:
                print("APK installation timed out. Please check the APK file and try again.")
                return

        # Verify installation
        if not self.is_app_installed(package_name):
            print("APK installation failed. Please check the path and try again.")
            return

        # Set up desired capabilities
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'sdk_gphone64_x86_64',  # Update the deviceName
            'appPackage': ' com.example.empty',
            'appActivity': ' com.example.empty.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
            'logLevel': 'debug'
        }

        # Start Appium server with JWT token
        appium_url = "http://127.0.0.1:4723/wd/hub"
        jwt_token = "your_jwt_token_here"  # Replace with your actual token
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        # Create a new session
        response = requests.post(appium_url + "/session", json={"desiredCapabilities": desired_caps}, headers=headers)

        if response.status_code == 200:
            session_id = response.json().get('sessionId')
            print(f"Session created successfully: {session_id}")
            self.driver = webdriver.Remote(appium_url, desired_caps)
            self.driver.implicitly_wait(50)
        else:
            print(f"Failed to create session: {response.json()}")

    def is_app_installed(self, package_name):
        """Check if the app is installed."""
        try:
            result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], 
                                    capture_output=True, text=True, check=True)
            return package_name in result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error checking app installation: {e.stderr}")
            return False

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
                return None

    def run_evaluation(self):
        self.setup_appium()
        # Add your evaluation logic here

    def cleanup(self):
        if self.driver:
            self.driver.quit()

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
    run_app_evaluation(29)  # Pass the index of your app here (0 for the first app)























"""
import os
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from analyzer.models import App 
import logging
import os
from datetime import datetime
import subprocess

class AppEvaluator:
    def __init__(self, apk_path):
        self.apk_path = "../app/build/outputs/apk/release/app-release-signed.apk"
        self.driver = None
        self.video_filename = "test_video.avi"
        self.video_writer = None

    def setup_appium(self):
        # 1. Install the APK if not already installed
        if not is_app_installed('com.example.finalanlyzer'):
            print("Installing APK...")
            subprocess.call(['adb', 'install', '-r', self.apk_path])

        # 2. Verify installation
        if not is_app_installed('com.example.finalanlyzer'):
            print("APK installation failed. Please check the path and try again.")
            return  # Or handle the error appropriately

        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'appPackage': 'com.example.finalanlyzer',
            'appActivity': 'com.example.finalanlyzer.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,  # Retain app data after session
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(50)

    # ... (rest of your class methods)


    def capture_ui_hierarchy(self):
        logging.debug("About to capture UI hierarchy")  # Use logging for structured messages
        try:
            ui_hierarchy = self.driver.page_source
            with open("ui_hierarchy.xml", "w") as f:
                f.write(ui_hierarchy)
            logging.info("UI hierarchy captured successfully") 
        except Exception as e:
            logging.error(f"Error capturing UI hierarchy: {e}")

            
def run_evaluation(self):
    print("Test execution started.")
    self.setup_appium()
    self.capture_ui_hierarchy()

    try:
        # Get the current state of the GUI before taking the screenshot
        original_ui_state = self.driver.page_source 

        # Simulate pressing Ctrl+S
        self.driver.press_keycode(21)  # Ctrl key
        self.driver.press_keycode(47)  # S key
        self.driver.keyevent(47)   # Release S key
        self.driver.keyevent(21)   # Release Ctrl key

        # Wait for the GUI to change after the screenshot action
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.page_source != original_ui_state
        )

        # Specify the directory where you want to save the screenshots
        screenshot_dir = "apk_analyzer/media/apk_files/screenshots$"  # Adjust this path as needed

        # Create the directory if it doesn't exist
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Generate a unique filename for the screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"screenshot_{timestamp}.png"

        # Construct the full path for saving the screenshot
        screenshot_path = os.path.join(screenshot_dir, screenshot_filename)

        # Now take the screenshot and save it to the specified path
        self.driver.save_screenshot(screenshot_path)

        print(f"Screenshot saved to: {screenshot_path}")
        logging.info(f"Screenshot saved to: {screenshot_path}")

        #  --- [Optional: Additional verification if needed] ---

        # Use WebDriverWait to wait for the screenshot file to appear (if necessary)
        WebDriverWait(self.driver, 600).until(
            lambda driver: os.path.exists(screenshot_path)
        )

        print("Screenshot verification complete. Screenshot found in the expected directory.")
        logging.info("Screenshot verification complete. Screenshot found in the expected directory.")

        # 4. Add assertions to verify the screenshot was taken successfully
        print("Verifying screenshot success...")
        logging.info("Verifying screenshot success...")

        # TODO: Implement your assertion logic here based on your app's behavior
        # For example, if your app displays a toast message:
        # WebDriverWait(self.driver, 10).until(
        #    EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.Toast[@text='Screenshot saved!']"))
        # )

        print("Screenshot verification complete.")
        logging.info("Screenshot verification complete.")
        
        # --- [End of Optional section] ---

    except AssertionError as e:
        self.take_screenshot("assertion_failure.png")  # Consider saving this to a different directory
        print(f"Assertion failed: {e}")
        raise e

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e 

    finally:
        self.take_screenshot("test_case_end.png")  # Consider saving this to a different directory
        print("Test execution completed.")
def run_app_evaluation(app_name):
    try:
        app = App.objects.get(name=app_name)  # Get the app by its name
        evaluator = AppEvaluator(app.apk_file_path)  # Use the apk_path from the app object
        evaluator.run_evaluation()
    except App.DoesNotExist:
        print(f"App with name '{app_name}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        evaluator.cleanup()

if __name__ == "__main__":
    run_app_evaluation("finalanlyzer")  # Pass the name of your app here


"""


"""
import os
import time
import cv2
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AppEvaluator:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.driver = None
        self.video_filename = "test_video.avi"
        self.video_writer = None

    def setup_appium(self):
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'app': self.apk_path,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(10)

    def capture_ui_hierarchy(self):
        ui_hierarchy = self.driver.page_source
        with open("ui_hierarchy.xml", "w") as file:
            file.write(ui_hierarchy)
        print("UI hierarchy captured.")

    def record_video(self):
        # Initialize video recording
        self.video_writer = cv2.VideoWriter(self.video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    def capture_screenshot(self, filename):
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")

    def simulate_button_click(self):
        # Locate the first button and click it
        first_button = self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[1]")  # Adjust as necessary
        first_button.click()
        print("Button clicked.")

    def check_screen_change(self):
        # Capture a screenshot after the click
        self.capture_screenshot("after_click.png")

        # Check if the screen changed (you can implement more sophisticated checks)
        # For simplicity, we'll just compare the two screenshots
        initial_screenshot = cv2.imread("initial_screen.png")
        after_click_screenshot = cv2.imread("after_click.png")
        
        # Simple comparison logic (you can enhance this)
        if (initial_screenshot != after_click_screenshot).any():
            return "Yes"
        return "No"

    def run_evaluation(self):
        self.setup_appium()
        self.capture_screenshot("initial_screen.png")
        self.capture_ui_hierarchy()
        self.record_video()
        
        # Simulate a button click
        self.simulate_button_click()
        
        # Check if the screen changed
        screen_changed = self.check_screen_change()
        print(f"Screen changed: {screen_changed}")
        
        # Save results to the database (implement your database logic here)
        # Example: save_to_database(ui_hierarchy, screen_changed)


def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None

    def cleanup(self):
        if self.video_writer:
            self.video_writer.release()
        self.driver.quit()
        print("Cleanup done.")


if __name__ == "__main__":
    evaluator = AppEvaluator("/home/hazem-elbatawy/AndroidStudioProjects/finalanlyzer/app/build/outputs/apk/release/app-release-unsigned.apk")
    try:
        evaluator.run_evaluation()
    finally:
        evaluator.cleanup()

"""






"""

import os
import time
import asyncio
from appium import webdriver
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import websockets
import json
import sys
from analyzer.models import App, AppiumTestResult

# WebSocket handler
async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

# Function to start the WebSocket server
def start_websocket_server():
    asyncio.run(websockets.serve(handler, "localhost", 8765))

class AppiumThread(QThread):
    def __init__(self):
        super().__init__()
        self.driver = None

    def setup_appium(self):
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'app': '/home/hazem-elbatawy/AndroidStudioProjects/finalanlyzer/app/build/outputs/apk/release/app-release-unsigned.apk',
            'appPackage': 'com.example.finalanalyzer',
            'appActivity': 'com.example.finalanalyzer.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(25)

    def grant_permissions(self, package_name):
        os.system(f'adb shell pm grant {package_name} android.permission.CAMERA')
        os.system(f'adb shell pm grant {package_name} android.permission.READ_EXTERNAL_STORAGE')

def capture_screenshot(self):
    screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)

    try:
        # Wait for a specific amount of time to let the UI settle
        time.sleep(5)  # Adjust the sleep duration as necessary

        # Alternatively, wait for an element that indicates the UI is ready
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.ID, 'com.example.finalanalyzer:id/greeting'))  # Replace with an actual element ID
        )

        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

    def run(self):
        self.setup_appium()
        self.capture_screenshot()

class MyWidget(QWidget):
    rgbcSensorValueChanged = pyqtSignal(int)
    postureChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.rgbcSensorValueWidget = QSlider()  # Example slider
        self.postureWidget = QSlider()  # Example slider for posture

        layout = QVBoxLayout()
        layout.addWidget(self.rgbcSensorValueWidget)
        layout.addWidget(self.postureWidget)
        self.setLayout(layout)

        self.rgbcSensorValueWidget.valueChanged.connect(self.on_rgbcSensorValueWidget_valueChanged)
        self.postureWidget.valueChanged.connect(self.on_posture_valueChanged)

    def on_rgbcSensorValueWidget_valueChanged(self, value):
        print(f"RGB Sensor Value Changed: {value}")

    def on_posture_valueChanged(self, posture):
        print(f"Posture Changed: {posture}")


def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None

# Example usage
if __name__ == "__main__":
    app = QApplication([])

    # Start the WebSocket server in a separate thread
    websocket_thread = QThread()
    websocket_thread.run = start_websocket_server
    websocket_thread.start()

    # Create and show the PyQt widget
    window = MyWidget()
    window.show()

    # Start the Appium thread
    appium_thread = AppiumThread()
    appium_thread.start()

    sys.exit(app.exec_())
"""

"""
import os
import time
import asyncio
from appium import webdriver
from django.core.files.base import ContentFile
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import websockets
from django.http import JsonResponse
import json
from analyzer.models import App, AppiumTestResult
from django.core.files import File
from django.utils import timezone
import signal
import sys
from PIL import Image, ImageChops
from appium.webdriver.common.mobileby import MobileBy


# WebSocket handler
async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

# Function to start the WebSocket server
def start_websocket_server():
    asyncio.run(websockets.serve(handler, "localhost", 8765))

class AppiumThread(QThread):
    def __init__(self):
        super().__init__()
        self.driver = None

    def setup_appium(self):
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'app': '/home/hazem-elbatawy/AndroidStudioProjects/finalanlyzer/app/build/outputs/apk/release/app-release-unsigned.apk',
            'appPackage': 'com.example.finalanalyzer',
            'appActivity': 'com.example.finalanalyzer.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(25)

    def grant_permissions(self, package_name):
        os.system(f'adb shell pm grant {package_name} android.permission.CAMERA')
        os.system(f'adb shell pm grant {package_name} android.permission.READ_EXTERNAL_STORAGE')

    def capture_screenshot(self):
        screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"screenshot_{int(time.time())}.png"
        screenshot_path = os.path.join(screenshot_dir, filename)

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'com.example.finalanalyzer:id/name:id/greeting'))  # Replace with an actual element ID
            )


            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def run(self):
        self.setup_appium()
        self.capture_screenshot()

class MyWidget(QWidget):
    rgbcSensorValueChanged = pyqtSignal(int)
    postureChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.rgbcSensorValueWidget = QSlider()  # Example slider
        self.postureWidget = QSlider()  # Example slider for posture

        layout = QVBoxLayout()
        layout.addWidget(self.rgbcSensorValueWidget)
        layout.addWidget(self.postureWidget)
        self.setLayout(layout)

        self.rgbcSensorValueWidget.valueChanged.connect(self.on_rgbcSensorValueWidget_valueChanged)
        self.postureWidget.valueChanged.connect(self.on_posture_valueChanged)

    def on_rgbcSensorValueWidget_valueChanged(self, value):
        print(f"RGB Sensor Value Changed: {value}")

    def on_posture_valueChanged(self, posture):
        print(f"Posture Changed: {posture}")

# Example usage
if __name__ == "__main__":
    app = QApplication([])

    # Start the WebSocket server in a separate thread
    websocket_thread = QThread()
    websocket_thread.run = start_websocket_server
    websocket_thread.start()

    # Create and show the PyQt widget
    window = MyWidget()
    window.show()

    # Start the Appium thread
    appium_thread = AppiumThread()
    appium_thread.start()

    app.exec_()

def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None

"""











"""
import os
import time
import asyncio
from appium import webdriver
from django.core.files.base import ContentFile
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import websockets
from django.http import JsonResponse
import json
from analyzer.models import App, AppiumTestResult
from django.core.files import File
from django.utils import timezone
import signal
import sys
from PIL import Image, ImageChops



# WebSocket handler
async def handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")

# Function to start the WebSocket server
def start_websocket_server():
    asyncio.run(websockets.serve(handler, "localhost", 8765))
    
class AppiumThread(QThread):
    def __init__(self):
        super().__init__()
        self.driver = None

    def setup_appium(self):
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'app': '/home/hazem-elbatawy/AndroidStudioProjects/finalanlyzer/app/build/outputs/apk/release/app-release-unsigned.apk',
            'appPackage': 'com.example.finalanalyzer',
            'appActivity': 'com.example.finalanalyzer.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(10)


def grant_permissions(package_name):
    os.system(f'adb shell pm grant {package_name} android.permission.CAMERA')
    os.system(f'adb shell pm grant {package_name} android.permission.READ_EXTERNAL_STORAGE')

    def capture_screenshot(self):
        screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"screenshot_{int(time.time())}.png"
        screenshot_path = os.path.join(screenshot_dir, filename)

        try:
            WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.ID, 'com.example.finalanalyzer:id/start_button'))  # Replace with an actual element ID
            )
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def run(self):
        self.setup_appium()
        self.capture_screenshot()

class MyWidget(QWidget):
    rgbcSensorValueChanged = pyqtSignal(int)
    postureChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.rgbcSensorValueWidget = QSlider()  # Example slider
        self.postureWidget = QSlider()  # Example slider for posture

        layout = QVBoxLayout()
        layout.addWidget(self.rgbcSensorValueWidget)
        layout.addWidget(self.postureWidget)
        self.setLayout(layout)

        self.rgbcSensorValueWidget.valueChanged.connect(self.on_rgbcSensorValueWidget_valueChanged)
        self.postureWidget.valueChanged.connect(self.on_posture_valueChanged)

    def on_rgbcSensorValueWidget_valueChanged(self, value):
        print(f"RGB Sensor Value Changed: {value}")

    def on_posture_valueChanged(self, posture):
        print(f"Posture Changed: {posture}")

 # Slot implementations
    def on_rgbcSensorValueWidget_valueChanged(self, value):
        print(f"RGB Sensor Value Changed: {value}")
# Example usage
if __name__ == "__main__":
    app = QApplication([])

    # Start the WebSocket server in a separate thread
    websocket_thread = QThread()
    websocket_thread.run = start_websocket_server
    websocket_thread.start()

    # Create and show the PyQt widget
    window = MyWidget()
    window.show()

    # Start the Appium thread
    appium_thread = AppiumThread()
    appium_thread.start()

    app.exec_()

def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None


"""


"""
import os
import time
from appium import webdriver
from django.core.files.base import ContentFile
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AppiumThread(QThread):
    def __init__(self):
        super().__init__()
        self.driver = None

class MyWidget(QWidget):
    # Define signals
    rgbcSensorValueChanged = pyqtSignal(int)
    postureChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        # Create UI elements
        self.rgbcSensorValueWidget = QSlider()  # Example slider
        self.postureWidget = QSlider()  # Example slider for posture

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.rgbcSensorValueWidget)
        layout.addWidget(self.postureWidget)
        self.setLayout(layout)

        # Connect signals to slots
        self.rgbcSensorValueWidget.valueChanged.connect(self.on_rgbcSensorValueWidget_valueChanged)
        self.postureWidget.valueChanged.connect(self.on_posture_valueChanged)

    # Slot implementations
    def on_rgbcSensorValueWidget_valueChanged(self, value):
        print(f"RGB Sensor Value Changed: {value}")

    def on_posture_valueChanged(self, posture):
        print(f"Posture Changed: {posture}")

class AppiumThread(QThread):
    def __init__(self):
        super().__init__()
        self.driver = None

    def setup_appium(self):
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'DjangoAPKAnalyzer',
            'app': '/home/hazem-elbatawy/AndroidStudioProjects/finalanlyzer/app/build/outputs/apk/release/app-release-unsigned.apk',
            'appPackage': 'com.example.finalanalyzer',
            'appActivity': 'com.example.finalanalyzer.MainActivity',
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        self.driver.implicitly_wait(10)
    def capture_screenshot(self):
        screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"screenshot_{int(time.time())}.png"
        screenshot_path = os.path.join(screenshot_dir, filename)

        try:
            # Use explicit wait to ensure the UI is ready
            WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.ID, 'com.example.finalanalyzer:id/start_button'))  # Replace with an actual element ID
            )
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    def run(self):
        self.setup_appium()
        # You can call capture_screenshot() here or based on some signal from the UI
        self.capture_screenshot()

# Example usage
if __name__ == "__main__":
    app = QApplication([])
    
    # Create and show the PyQt widget
    window = MyWidget()
    window.show()

    # Start the Appium thread
    appium_thread = AppiumThread()
    appium_thread.start()

    app.exec_()


def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None


"""
"""

from django.http import JsonResponse
import json
from analyzer.models import App, AppiumTestResult
import os
import time
from django.core.files import File
from django.utils import timezone
import signal
import sys
from PIL import Image, ImageChops
import subprocess
from appium import webdriver

def start_appium_server(log_level='debug'):
    command = f'appium --log-level {log_level}'
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)  # Allow time for the server to start
    return process

def grant_permissions(package_name):
    os.system(f'adb shell pm grant {package_name} android.permission.CAMERA')
    os.system(f'adb shell pm grant {package_name} android.permission.READ_EXTERNAL_STORAGE')

def setup_appium(avd_name):
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '10.0',
        'deviceName': 'DjangoAPKAnalyzer',
        'app': '/home/hazem-elbatawy/AndroidStudioProjects/Demozozapp/app/build/outputs/apk/debug/app-debug.apk',
        'appPackage': 'com.example.demozozapp',
        'appActivity': 'com.example.demozozapp.MainActivity',
        'autoGrantPermissions': True,
        'automationName': 'UiAutomator2',
        'noReset': True,
        'fullReset': False,
    }
    return webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

def start_emulator(avd_name):
    command = f'emulator -avd {avd_name} -gpu swiftshader_indirect'
    process = subprocess.Popen(command, shell=True)
    time.sleep(50)  # Adjust time as necessary
    return process

def capture_screenshot(driver):
    screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)

    time.sleep(5)  # Wait for the UI to settle
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def start_video_recording():
    video_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/videos'
    os.makedirs(video_dir, exist_ok=True)
    filename = f"screenrecord_{int(time.time())}.mp4"
    video_path = os.path.join(video_dir, filename)
    
    os.system(f'adb shell screenrecord {video_path} &')
    print(f"Video recording started, saving to: {video_path}")
    return video_path

def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None

    try:
        appium_process = start_appium_server('debug')
        driver = setup_appium("DjangoAPKAnalyzer")
        grant_permissions(app.appPackage)  # Ensure permissions are granted

        # Capture UI hierarchy
        app.ui_hierarchy = driver.page_source

        # Simulate user actions
        screenshot_button = driver.find_element("id", '22')  # Update with actual ID
        record_button = driver.find_element("id", 'your_record_button_id')  # Update with actual ID
        first_screenshot_path = capture_screenshot(driver)

        screenshot_button.click()
        time.sleep(1)  # Wait for the screenshot to be taken
        first_screenshot_path = capture_screenshot(driver)

        record_button.click()
        video_path = start_video_recording()
        time.sleep(10)  # Record for a specified duration
        os.system('adb shell killall screenrecord')  # Stop the recording

        second_screenshot_path = capture_screenshot(driver)
        save_test_result(app, first_screenshot_path, second_screenshot_path, video_path)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        if appium_process:
            stop_appium_server(appium_process)

def images_are_different(img1_path, img2_path):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None

def save_test_result(app, initial_screenshot_path, subsequent_screenshot_path, video_path):
    screen_changed = images_are_different(initial_screenshot_path, subsequent_screenshot_path)

    try:
        with open(initial_screenshot_path, 'rb') as initial_file:
            initial_screenshot = File(initial_file)

            with open(subsequent_screenshot_path, 'rb') as subsequent_file:
                subsequent_screenshot = File(subsequent_file)

                result = AppiumTestResult(
                    app=app,
                    screen_changed=screen_changed,
                    initial_screenshot=initial_screenshot,
                    subsequent_screenshot=subsequent_screenshot,
                    created_at=timezone.now()
                )
                result.save()
                print("Test result saved successfully.")

                if os.path.exists(video_path):
                    with open(video_path, 'rb') as video_file:
                        video_file_data = File(video_file)
                        result.video = video_file_data  # Assuming you have a field for video
                        result.save()
                        print("Video saved successfully.")
    except Exception as e:
        print(f"Error saving test result: {e}")

def stop_appium_server(process):
    process.terminate()

def signal_handler(sig, frame):
    print('Signal received, cleaning up...')
    sys.exit(0)

def run_appium_test(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = data.get('app_id')

        run_app_evaluation(app_id)

        return JsonResponse({'output': 'Test completed successfully.'})

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run_app_evaluation(app_id=1)  # Example app_id
    finally:
        if 'driver' in locals():
            driver.quit()


"""






"""

from django.http import JsonResponse
import json
from analyzer.models import App, AppiumTestResult  # Adjust this import as necessary
import os
import time
from django.core.files import File
from django.utils import timezone
import signal
import sys
from PIL import Image, ImageChops
import subprocess
from appium import webdriver  # Keep this for mobile testing


def start_appium_server(log_level='debug'):
    # Start Appium server with specified log level
    command = f'appium --log-level {log_level}'
    process = subprocess.Popen(command, shell=True)
    
    # Give the server some time to start
    time.sleep(5)
    return process

    def grant_permissions():
    os.system('adb shell pm grant your.package.name android.permission.CAMERA')
    os.system('adb shell pm grant your.package.name android.permission.READ_EXTERNAL_STORAGE')

def setup_appium(avd_name):
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '10.0',  # For API 24 (Nougat)
        'deviceName': 'DjangoAPKAnalyzer',
        'app': '/home/hazem-elbatawy/AndroidStudioProjects/Demozozapp/app/build/outputs/apk/debug/app-debug.apk',
        'appPackage': 'com.example.demozozapp',  # Correct package name
        'appActivity': 'com.example.demozozapp.MainActivity',  # Use your MainActivity here
        'autoGrantPermissions': True,  # Automatically grant permissions
        'automationName': 'UiAutomator2',
        "noReset": True,
        "fullReset": False,
    }




def start_emulator(avd_name):
    # Start the Android emulator with no authentication, gRPC, and no snapshot load
    command = f'emulator -avd {avd_name} -grpc -no-snapshot-load -gpu swiftshader_indirect -no-auth'
    process = subprocess.Popen(command, shell=True)
    
    # Give the emulator some time to start
    time.sleep(30)  # Adjust time as necessary for your emulator to boot
    return process


def capture_screenshot(driver):
    # Create a timestamp for the screenshot file name
    timestamp = int(time.time())
    
    # Define the directory to save screenshots
    screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
    
    # Create the directory if it doesn't exist
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Create the screenshot file name
    filename = f"screenshot_{timestamp}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)
    
    try:
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

    return screenshot_path

def start_video_recording():
    video_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/videos'
    os.makedirs(video_dir, exist_ok=True)
    filename = f"screenrecord_{int(time.time())}.mp4"
    video_path = os.path.join(video_dir, filename)
    
    os.system(f'adb shell screenrecord {video_path} &')
    print(f"Video recording started, saving to: {video_path}")
    return video_path

def start_emulator(avd_name):
    # Start the Android emulator
    command = f'emulator -avd {avd_name} -gpu swiftshader_indirect'
    process = subprocess.Popen(command, shell=True)
    
    # Give the emulator some time to start
    time.sleep(50)  # Adjust time as necessary for your emulator to boot
    return process

def run_app_evaluation(app_id):
    app = App.objects.get(id=app_id)
    driver = None
    appium_process = None
    check_permissions(driver)  # Implement this function to check permissions

     # Load the JSON configuration
    config_path = os.path.join('analyzer', 'config.json')  # Adjust path as necessary
    with open(config_path) as json_file:
        config_data = json.load(json_file)

    try:
        appium_process = start_appium_server('debug')  # Start Appium server with debug level
        driver = setup_appium("DjangoAPKAnalyzer")
        
        # Capture UI hierarchy
        app.ui_hierarchy = driver.page_source
        
        # Simulate user clicks on buttons
        screenshot_button = driver.find_element("id", '22')  # Update with actual ID
        record_button = driver.find_element("id", 'your_record_button_id')  # Update with actual ID
        capture_screenshot(driver)

        # Click the screenshot button
        screenshot_button.click()
        time.sleep(1)  # Wait for the screenshot to be taken
        first_screenshot_path = capture_screenshot(driver)

        # Click the record button and start video recording
        record_button.click()
        video_path = start_video_recording()  # Start video recording
        time.sleep(10)  # Record for a specified duration
        
        # Stop the screen recording
        os.system('adb shell killall screenrecord')  # Use killall to stop the recording

        # Capture second screenshot after recording
        second_screenshot_path = capture_screenshot(driver)

        # Define paths for screenshots and video
        screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
        video_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/videos'
        
        # Ensure directories exist
        os.makedirs(screenshot_dir, exist_ok=True)
        os.makedirs(video_dir, exist_ok=True)

        # Define full paths for the screenshots and video
        first_screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time())}.png")
        second_screenshot_path = os.path.join(screenshot_dir, f"screenshot_{int(time.time()) + 1}.png")  # Just an example
        video_path = os.path.join(video_dir, f"screenrecord_{int(time.time())}.mp4")

        # Save results to the database
        save_test_result(app, first_screenshot_path, second_screenshot_path, video_path)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()  # Ensure the driver is closed
        if appium_process:
            stop_appium_server(appium_process)  # Stop the Appium server if it was started

def images_are_different(img1_path, img2_path):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None  # Returns True if images are different

def save_test_result(app, initial_screenshot_path, subsequent_screenshot_path, video_path):
    screen_changed = images_are_different(initial_screenshot_path, subsequent_screenshot_path)

    try:
        with open(initial_screenshot_path, 'rb') as initial_file:
            initial_screenshot = File(initial_file)

            with open(subsequent_screenshot_path, 'rb') as subsequent_file:
                subsequent_screenshot = File(subsequent_file)

                result = AppiumTestResult(
                    app=app,
                    screen_changed=screen_changed,
                    initial_screenshot=initial_screenshot,
                    subsequent_screenshot=subsequent_screenshot,
                    created_at=timezone.now()
                )

                result.save()
                print("Test result saved successfully.")

                # Save video if it exists
                if os.path.exists(video_path):
                    with open(video_path, 'rb') as video_file:
                        video_file_data = File(video_file)
                        result.video = video_file_data  # Assuming you have a field for video
                        result.save()  # Save the updated result with the video
                        print("Video saved successfully.")
    except Exception as e:
        print(f"Error saving test result: {e}")

def signal_handler(sig, frame):
    print('Signal received, cleaning up...')
    sys.exit(0)

def end_test(driver):
    screenshot_path = capture_screenshot(driver)
    driver.quit()
    return screenshot_path

# New view for running Appium tests
def run_appium_test(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = data.get('app_id')

        # Call the run_app_evaluation function with the app_id
        run_app_evaluation(app_id)

        return JsonResponse({'output': 'Test completed successfully.'})  # Adjust as necessary


def capture_screenshot(driver):
    screenshot_dir = '/home/hazem-elbatawy/Downloads/apk_analyzer/media/apk_files/screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)

    time.sleep(5)  # Wait for the UI to settle


    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None  # Return None if there's an error
    return screenshot_path


def stop_appium_server(process):
    # Stop the Appium server process
    process.terminate()  # or process.kill() if needed
# Main execution block (if applicable)

if __name__ == "__main__":
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Example app_id; replace with actual ID
        run_app_evaluation(app_id=1)  
    finally:
        if 'driver' in locals():
            end_test(driver)
"""