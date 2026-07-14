"""Tests for the analyzer app.

Run with:  python manage.py test
The Appium/emulator pipeline itself needs real devices, so these tests
cover everything below it: authentication and ownership rules on every
view, APK upload, and the screenshot-comparison/persistence helpers.
"""
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from analyzer.models import App, AppiumTestResult
from appium_tests.appium_test import images_are_different, save_test_result

MEDIA_TMP = tempfile.mkdtemp(prefix='apkanalyzer-test-media-')


def make_png(path, color):
    Image.new('RGB', (32, 32), color).save(path)
    return path


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class ViewAuthTests(TestCase):
    """Every app view requires login; object views require ownership."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('owner', password='test-pass-123')
        cls.intruder = User.objects.create_user('intruder', password='test-pass-123')
        cls.app = App.objects.create(name='Demo', uploaded_by=cls.owner)

    def test_index_redirects_anonymous_to_login(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_app_detail_requires_login(self):
        response = self.client.get(reverse('app_detail', args=[self.app.id]))
        self.assertEqual(response.status_code, 302)

    def test_app_detail_owner_can_view(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('app_detail', args=[self.app.id]))
        self.assertEqual(response.status_code, 200)

    def test_app_detail_other_user_gets_404(self):
        # Regression: app_detail used to be reachable without ownership
        # (a duplicate definition had dropped @login_required entirely).
        self.client.force_login(self.intruder)
        response = self.client.get(reverse('app_detail', args=[self.app.id]))
        self.assertEqual(response.status_code, 404)

    def test_delete_requires_login(self):
        # Regression: delete_item used to have no auth at all — anyone
        # could delete any app with a single POST.
        response = self.client.post(reverse('delete_item', args=[self.app.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(App.objects.filter(id=self.app.id).exists())

    def test_delete_other_users_app_forbidden(self):
        self.client.force_login(self.intruder)
        response = self.client.post(reverse('delete_item', args=[self.app.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(App.objects.filter(id=self.app.id).exists())

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('delete_item', args=[self.app.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(App.objects.filter(id=self.app.id).exists())

    def test_edit_other_users_app_forbidden(self):
        # Regression: edit_item required login but never checked ownership.
        self.client.force_login(self.intruder)
        response = self.client.get(reverse('edit_item', args=[self.app.id]))
        self.assertEqual(response.status_code, 404)

    def test_run_appium_test_rejects_get(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('run_appium_test'))
        self.assertEqual(response.status_code, 405)


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class UploadTests(TestCase):
    def test_upload_apk_creates_owned_app(self):
        user = User.objects.create_user('uploader', password='test-pass-123')
        self.client.force_login(user)
        apk = SimpleUploadedFile('demo.apk', b'PK\x03\x04fake-apk-bytes')
        response = self.client.post(
            reverse('create_item'), {'name': 'Uploaded app', 'apk_file_path': apk}
        )
        self.assertEqual(response.status_code, 302)
        app = App.objects.get(name='Uploaded app')
        self.assertEqual(app.uploaded_by, user)
        self.assertTrue(app.apk_file_path.name.endswith('.apk'))


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class EvaluationHelperTests(TestCase):
    """The screenshot-comparison and persistence layer, no emulator needed."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='apkanalyzer-shots-')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.user = User.objects.create_user('runner', password='test-pass-123')
        self.app = App.objects.create(name='Evaluated', uploaded_by=self.user)

    def test_identical_images_are_not_different(self):
        a = make_png(f'{self.tmp}/a.png', 'white')
        b = make_png(f'{self.tmp}/b.png', 'white')
        self.assertFalse(images_are_different(a, b))

    def test_changed_images_are_different(self):
        a = make_png(f'{self.tmp}/a.png', 'white')
        b = make_png(f'{self.tmp}/b.png', 'black')
        self.assertTrue(images_are_different(a, b))

    def test_save_test_result_persists_run(self):
        first = make_png(f'{self.tmp}/first.png', 'white')
        second = make_png(f'{self.tmp}/second.png', 'red')

        result = save_test_result(
            self.app, first, second, 'Test completed.', ui_hierarchy='<hierarchy/>'
        )

        stored = AppiumTestResult.objects.get(id=result.id)
        self.assertEqual(stored.app, self.app)
        self.assertTrue(stored.screen_changed)
        self.assertEqual(stored.log, 'Test completed.')
        self.assertTrue(stored.initial_screenshot.name)
        self.assertTrue(stored.subsequent_screenshot.name)
        self.assertEqual(list(self.app.test_results.all()), [stored])

    def test_save_test_result_detects_unchanged_screen(self):
        first = make_png(f'{self.tmp}/first.png', 'blue')
        second = make_png(f'{self.tmp}/second.png', 'blue')
        result = save_test_result(self.app, first, second, 'No change.')
        self.assertFalse(result.screen_changed)
