# Deep INK Community Centre Management System

## Project Overview

The Deep INK Community Centre Management System is a Django-based web application developed as part of a Work-Integrated Learning project.

The system consists of:

- A public community-centre website
- Volunteer and service-request forms
- A secure staff portal
- Role-based access control
- Two-factor authentication
- A central CRM dashboard
- Community programme and beneficiary management
- Microsoft Azure deployment
- Azure Database for PostgreSQL integration

## Live Deployment

The application is deployed using Microsoft Azure App Service:

https://deepinkcommunity-app-fkhhbrhngyd4b3cq.uaenorth-01.azurewebsites.net/

## Main Features

### Public Website

- Home page
- About page
- Programmes page
- Get Involved page
- Contact page
- Volunteer application submission
- Public service-request submission
- Responsive navigation and page layouts

### Staff Authentication and Security

- Secure username and password authentication
- Time-based one-time password two-factor authentication
- QR-code authenticator enrolment
- Single-use recovery codes
- Role-based authorisation
- Protected dashboard and administration pages
- Session expiry controls
- CSRF protection
- Environment-based secret management

### CRM and Administration

- Beneficiary management
- Service-request management
- Programme management
- Programme enrolments
- Attendance tracking
- Referrals
- Volunteer records
- Partner records
- Donor records
- Emerging entrepreneur records
- Donations and funding records
- Outreach distribution records
- Document management
- Staff tasks
- Follow-up records
- Audit logs
- Staff account management

## User Roles

The system supports the following roles:

- **Administrator** – manages staff accounts, permissions and system information
- **Manager** – manages operational information and staff activities
- **Staff** – accesses authorised CRM and community-management functions

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap
- Bootstrap Icons

### Backend

- Python 3.12
- Django
- Django authentication
- Django groups and permissions
- django-otp
- QRCode

### Database

- SQLite for local development
- Azure Database for PostgreSQL in production
- psycopg PostgreSQL driver
- dj-database-url

### Deployment

- Microsoft Azure App Service
- Azure Database for PostgreSQL
- GitHub Actions
- Gunicorn
- WhiteNoise

### Development Tools

- Visual Studio Code
- Git
- GitHub

## Project Structure

```text
DeepINKCommunity/
├── DeepINKCommunity/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── accounts/
│   ├── management/
│   ├── migrations/
│   ├── templates/accounts/
│   ├── forms.py
│   ├── models.py
│   ├── two_factor_views.py
│   ├── urls.py
│   └── views.py
├── app/
│   ├── migrations/
│   ├── static/
│   ├── templates/app/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── dashboard/
│   ├── migrations/
│   ├── templates/dashboard/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/deepinkcom/DeepINKCommunity.git
cd DeepINKCommunity
```

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create User Roles

```bash
python manage.py create_roles
```

### 6. Configure Permissions

```bash
python manage.py setup_permissions
```

### 7. Create an Administrator

```bash
python manage.py createsuperuser
```

### 8. Run the Application

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Two-Factor Authentication

After a staff member successfully enters their username and password:

1. The user is directed to two-factor authentication.
2. A first-time user scans the displayed QR code using an authenticator application.
3. The user enters the generated six-digit code.
4. Recovery codes are provided for emergency access.
5. Each recovery code can only be used once.
6. A verified user is redirected to the authorised dashboard.

Authenticator secrets, QR codes and recovery codes must never be committed to GitHub or included in screenshots.

## Environment Variables

Production configuration is provided through Azure App Service environment variables.

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
DATABASE_URL
```

Example development values:

```text
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Production passwords, database connection strings, secret keys, OTP secrets and recovery codes must never be committed to the repository.

## Database Configuration

When `DATABASE_URL` is not present, the application uses SQLite for local development.

In production, `DATABASE_URL` contains the Azure PostgreSQL connection string. Django reads the connection using `dj-database-url`, and secure PostgreSQL connections require SSL.

## Static Files

Static files are collected for production with:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves the collected static files through the deployed Django application.

## Validation and Testing

The following final checks were completed:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Results:

```text
System check identified no issues (0 silenced).
No changes detected.
No migrations to apply.
```

The following functionality was also tested:

- All five public pages load successfully
- Volunteer applications generate reference numbers
- Submitted applications are stored in the database
- Staff password authentication works
- Authenticator codes are accepted
- Invalid codes are rejected
- Recovery codes are single-use
- Dashboard pages require authentication
- Django administration is protected by two-factor authentication

## Azure Deployment

The application is deployed through GitHub Actions to Microsoft Azure App Service.

The deployment process:

1. Changes are developed on a feature branch.
2. A pull request is created.
3. Team members review the pull request.
4. Approved changes are merged into `main`.
5. GitHub Actions deploys the application to Azure.
6. Database migrations are applied to Azure PostgreSQL.
7. Static files are collected for production.

## Useful Commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py collectstatic --noinput
python manage.py runserver
python manage.py create_roles
python manage.py setup_permissions
python manage.py createsuperuser
```

## Development and Security Rules

1. Never commit passwords, secret keys, database URLs or access tokens.
2. Never commit authenticator secrets, QR codes or recovery codes.
3. Do not commit `db.sqlite3`.
4. Do not commit the virtual environment.
5. Develop new work on a dedicated branch.
6. Pull the latest `main` branch before starting work.
7. Use descriptive commit messages.
8. Test changes locally before pushing them.
9. Require team review before merging pull requests.
10. Run `python manage.py check` before committing.
11. Store production configuration in Azure environment variables.
12. Keep the Google Search Console verification tag in the website layout.