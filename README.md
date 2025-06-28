# GSEZ Profile Management System

A comprehensive profile management system for Global Special Economic Zone (GSEZ) with different user roles (user, admin, HR, security) and features.

## Features

### Common Features

- Common login system for all user types (user, admin, HR, security)
- User registration system
- Role-based redirects after login
- Profile management
- Password change and reset functionality

### User Features

- Dashboard with emergency contacts and basic information
- Profile editing
- Profile card with QR code
- Job opportunities browsing and application
- Password management

### Admin Features

- User management (view, edit, create, delete, deactivate, block, etc.)
- QR code management
- Company management
- HR management with company assignment
- Security personnel management
- Job management
- Data export to Excel/CSV

### HR Features

- Company details management
- Job posting management
- Job inquiry handling
- Profile management

### Security Features

- QR code scanning functionality
- User details viewing
- User registration

## Technical Stack

- **Backend**: Django 3.2
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (recommended for production)
- **Additional Libraries**:
  - django-crispy-forms for form rendering
  - Pillow for image processing
  - QRCode for generating QR codes
  - XLWT and OpenPyXL for Excel export

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Apply migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python create_superuser.py
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Access the application at `http://127.0.0.1:8000/`

## Default Superuser Credentials

- Username: admin
- Password: admin123

## Data Models

### User Model

- Personal information (name, nationality, date of birth, etc.)
- Contact information (emergency contacts, family members)
- Address information
- Employment information (current and previous)
- Education information
- Status and verification details
- QR code

### Company Model

- Company name

### Document Model

- Government ID information
- ID photos

## License

This project is licensed under the MIT License.
