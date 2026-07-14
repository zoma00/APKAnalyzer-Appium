"""Appium-driven APK evaluation.

Drives an Android emulator through the Appium server: installs the APK
over adb, captures a screenshot before and after interacting with the
app, and persists both screenshots plus a log to the AppiumTestResult
model. Requires a running Appium server and the DjangoAPKAnalyzer AVD;
the pure helpers (images_are_different, save_test_result) are unit
tested without an emulator.
"""
import logging
import os
import subprocess
import time
from xml.etree import ElementTree
from zipfile import ZipFile

from appium import webdriver
from django.conf import settings
from django.core.files import File
from PIL import Image, ImageChops

from analyzer.models import App, AppiumTestResult

logger = logging.getLogger(__name__)

APPIUM_URL = 'http://127.0.0.1:4723/wd/hub'


class AppEvaluator:
    def __init__(self, apk_path):
        self.apk_path = os.path.join(settings.MEDIA_ROOT, str(apk_path))
        self.driver = None

    def setup_appium(self, package_name='com.example.Button'):
        if not os.path.exists(self.apk_path):
            raise FileNotFoundError(f'APK file does not exist at {self.apk_path}')

        if not self.is_app_installed(package_name):
            logger.info('Installing APK %s ...', self.apk_path)
            subprocess.run(
                ['adb', 'install', '-r', self.apk_path],
                capture_output=True, text=True, check=True, timeout=60,
            )

        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'sdk_gphone64_x86_64',
            'appPackage': package_name,
            'autoGrantPermissions': True,
            'automationName': 'UiAutomator2',
            'noReset': True,
        }
        self.driver = webdriver.Remote(APPIUM_URL, desired_caps)
        self.driver.implicitly_wait(50)

    def is_app_installed(self, package_name):
        """Check whether the package is installed on the device/emulator."""
        try:
            result = subprocess.run(
                ['adb', 'shell', 'pm', 'list', 'packages'],
                capture_output=True, text=True, check=True,
            )
            return package_name in result.stdout
        except subprocess.CalledProcessError as e:
            logger.error('Error checking app installation: %s', e.stderr)
            return False

    def get_main_activity_from_apk(self):
        with ZipFile(self.apk_path, 'r') as zip_ref:
            try:
                manifest_data = zip_ref.read('AndroidManifest.xml')
                manifest_tree = ElementTree.fromstring(manifest_data)
                application_node = manifest_tree.find('application')

                for activity_node in application_node.findall('activity'):
                    intent_filter_node = activity_node.find('intent-filter')
                    if intent_filter_node is None:
                        continue
                    for action_node in intent_filter_node.findall('action'):
                        if action_node.get('android:name') != 'android.intent.action.MAIN':
                            continue
                        for category_node in intent_filter_node.findall('category'):
                            if category_node.get('android:name') == 'android.intent.category.LAUNCHER':
                                return activity_node.get('android:name')
            except Exception as e:
                logger.error('Error extracting main activity from APK: %s', e)
                return None

    def capture_screenshot(self, tag):
        screenshot_dir = os.path.join(settings.MEDIA_ROOT, 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        path = os.path.join(screenshot_dir, f'{tag}_{int(time.time() * 1000)}.png')
        self.driver.save_screenshot(path)
        logger.info('Screenshot saved to %s', path)
        return path

    def run_evaluation(self):
        """Capture a before/after screenshot pair and the UI hierarchy."""
        self.setup_appium()
        initial_screenshot = self.capture_screenshot('initial')
        ui_hierarchy = self.driver.page_source

        # Interact with the app so the second capture can differ from
        # the first (press the first button on screen if there is one).
        try:
            button = self.driver.find_element(
                'xpath', '//android.widget.Button[1]'
            )
            button.click()
            time.sleep(1)
        except Exception:
            logger.info('No button found to interact with; capturing as-is.')

        subsequent_screenshot = self.capture_screenshot('subsequent')
        return initial_screenshot, subsequent_screenshot, ui_hierarchy

    def cleanup(self):
        if self.driver:
            self.driver.quit()


def images_are_different(img1_path, img2_path):
    """True when the two images differ in any pixel."""
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    diff = ImageChops.difference(img1, img2)
    return diff.getbbox() is not None


def save_test_result(app, initial_screenshot_path, subsequent_screenshot_path,
                     log_output, ui_hierarchy=''):
    """Persist an evaluation run (screenshots, change flag, log) to the DB."""
    screen_changed = images_are_different(
        initial_screenshot_path, subsequent_screenshot_path
    )

    with open(initial_screenshot_path, 'rb') as initial_file, \
            open(subsequent_screenshot_path, 'rb') as subsequent_file:
        result = AppiumTestResult(
            app=app,
            ui_hierarchy=ui_hierarchy,
            screen_changed=screen_changed,
            log=log_output,
        )
        result.initial_screenshot.save(
            os.path.basename(initial_screenshot_path), File(initial_file), save=False
        )
        result.subsequent_screenshot.save(
            os.path.basename(subsequent_screenshot_path), File(subsequent_file), save=False
        )
        result.save()
    return result


def run_app_evaluation(app_id):
    """Evaluate the app with the given primary key and store the result."""
    app = App.objects.get(id=app_id)
    evaluator = AppEvaluator(app.apk_file_path.name)
    log_output = 'Test started...\n'
    try:
        initial, subsequent, ui_hierarchy = evaluator.run_evaluation()
        log_output += 'Screenshots captured.\nTest completed successfully.'
        return save_test_result(app, initial, subsequent, log_output, ui_hierarchy)
    except Exception as e:
        logger.error('Evaluation failed for app %s: %s', app_id, e)
        raise
    finally:
        evaluator.cleanup()
