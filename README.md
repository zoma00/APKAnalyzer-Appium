# APKAnalyzer-Appium
This project is a full-stack web application developed using Django and MySQL, designed to manage and test Android APKs. The application leverages Appium for automated testing, providing users with a platform to upload, evaluate, and manage their applications.

Here’s a comprehensive README file for your project titled "Full-Stack Web Application with Django and Appium":


# Full-Stack Web Application with Django and Appium

## Challenge Overview
This project is a full-stack web application developed using Django and MySQL, designed to manage and test Android APKs. The application leverages Appium for automated testing, providing users with a platform to upload, evaluate, and manage their applications.

## Table of Contents
- [Features](#features)
- [Project Requirements](#project-requirements)
- [Technical Specifications](#technical-specifications)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Authentication and Management**: Secure user registration and login functionalities.
- **App Management**: Users can list, add, update, and delete their uploaded apps.
- **Automated App Evaluation**: Integrates Appium to automate the testing of APKs on an Android emulator.
- **Accessibility Features**: Options for font size adjustments and high contrast mode.
- **Multilingual Support**: Supports English and French languages.

## Project Requirements
1. **User Authentication and Management**:
   - Implement user registration and login functionalities using Django's built-in authentication system.

2. **App Management**:
   - List, add, update, and delete apps with various attributes (id, name, uploaded_by, etc.).
   - Upload APK files and run Appium tests.

3. **App Evaluation with Appium**:
   - Launch an Android emulator, install the APK, and capture UI elements.
   - Store screenshots, video recordings, and UI elements hierarchy in the database.

4. **Accessibility Features**:
   - Options for font size adjustments and high contrast mode.

5. **Multilingual Support**:
   - Bilingual functionality with dynamic language switching.

## Technical Specifications
- **Deployment**: Docker (includes Dockerfile and docker-compose.yaml)
- **Backend**: Django with MySQL
- **Frontend**: Django Templates, HTML, CSS, JavaScript
- **Automated Testing**: Appium
- **Accessibility**: CSS and JavaScript for accessibility features
- **Multilingual Support**: Django’s internationalization framework
- **Quality Control**: Django Unit Tests

## Installation
To set up the project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/full-stack-web-app.git
   cd full-stack-web-app
   ```

2. **Build and run the Docker containers**:
   ```bash
   docker-compose up --build
   ```

3. **Migrate the database**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create a superuser** (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Usage
Once the application is running, you can access it at `http://localhost:8000`. 

- **User Registration/Login**: Create an account or log in to manage your apps.
- **App Management**: Upload your APK files and run tests.
- **Accessibility Options**: Adjust font sizes and enable high contrast mode.
- **Language Switching**: Toggle between English and French.

## Testing
To run tests for the application, use the following command:

```bash
appiumtest.py
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.



For any questions or feedback, please contact [your email address].
Author:
---------
Hazem Elbatawy 

