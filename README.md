# APK Analyzer — Django + Appium

![CI](https://github.com/zoma00/APKAnalyzer-Appium/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django%204.2-092E20?logo=django&logoColor=white)
![Appium](https://img.shields.io/badge/Appium-663399?logo=appium&logoColor=white)
![Android](https://img.shields.io/badge/Android%20Emulator-3DDC84?logo=android&logoColor=white)

A Django web platform that manages uploaded Android APKs and drives
automated UI evaluations against an Android emulator through Appium.
For each run it installs the APK over `adb`, captures a screenshot
before and after interacting with the app, detects whether the screen
changed, and stores the screenshots, UI hierarchy, and run log in the
database — browsable per app in the web UI.

## How it works

```text
Browser ──> Django (upload APK, per-user app management)
                │
                ▼
        run_appium_test view
                │  starts Appium server + Android emulator if needed
                │  installs the APK via adb
                ▼
        appium_tests/appium_test.py
                │  Appium WebDriver session against the emulator
                │  screenshot → interact → screenshot
                ▼
        AppiumTestResult (screenshots, screen_changed, UI hierarchy, log)
```

## Features

- User registration and login (Django auth)
- Per-user APK management: upload, edit, delete — all owner-scoped
  (users can only see and modify their own apps)
- One-click Appium evaluation from the web UI
- Before/after screenshot capture with pixel-level change detection
  (Pillow `ImageChops`)
- Evaluation history per app: screenshots, change flag, and logs
  persisted in the `AppiumTestResult` model

## Requirements

- Python 3.10+
- [Appium server](https://appium.io/) (`npm install -g appium`)
- Android SDK with `adb`, the emulator, and an AVD named
  `DjangoAPKAnalyzer`
- SQLite works out of the box; for MySQL set `DB_ENGINE=mysql` and the
  `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT`
  environment variables (and `pip install mysqlclient`)

## Setup

```bash
git clone https://github.com/zoma00/APKAnalyzer-Appium.git
cd APKAnalyzer-Appium
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://localhost:8000>, register an account, upload an APK, and
start an evaluation from the app's page (the Appium server and emulator
must be available on the machine running Django).

## Tests

```bash
python manage.py test
```

The suite covers authentication and ownership rules on every view, APK
upload, and the screenshot-comparison/persistence layer. The Appium
pipeline itself requires a real emulator, so it is exercised manually
rather than in CI.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | insecure dev key | Set in production |
| `DEBUG` | `1` | Set `DEBUG=0` in production |
| `DB_ENGINE` | sqlite | `mysql` switches to MySQL via `DB_*` vars |

## Project structure

```text
analyzer/            # Django app: models, views, forms, templates
  models.py          # App (uploaded APKs), AppiumTestResult (runs)
  views.py           # Auth-protected, owner-scoped CRUD + test trigger
appium_tests/
  appium_test.py     # AppEvaluator, screenshot diffing, result saving
apk_analyzer/        # Django project settings and URLs
templates/analyzer/  # Web UI
```

## License

[MIT](LICENSE)

Author: Hazem Elbatawy
