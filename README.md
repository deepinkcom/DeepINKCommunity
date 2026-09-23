\# Deep INK Community Centre Management System



\## Project Overview



The Deep INK Community Centre Management System is a web-based platform being developed as part of a Work-Integrated Learning (WIL) project.



The system is designed to support the digital management of the Deep INK Community Centre by providing secure staff access, role-based permissions, a central dashboard, and functionality that can be integrated with the organisation's future community and CRM requirements.



The project uses a modular architecture so that different development team members can work on separate functional areas while maintaining a common Django application.



\---



\## Project Objectives



The main objectives of the system are to:



\- Provide secure staff authentication.

\- Manage staff accounts and staff information.

\- Implement role-based access control.

\- Provide different levels of permissions for administrators, managers and staff.

\- Provide a central dashboard for authorised users.

\- Support future CRM functionality.

\- Improve the organisation's ability to manage community information and activities.

\- Provide a maintainable and scalable foundation for future deployment.



\---



\## Technology Stack



\### Frontend



\- HTML5

\- CSS3

\- Bootstrap

\- JavaScript

\- Bootstrap Icons



\### Backend



\- Python

\- Django

\- Django Authentication

\- Django Groups and Permissions



\### Database



\- SQLite for local development

\- Azure SQL Database or PostgreSQL planned for production



\### Development Tools



\- Visual Studio

\- Git

\- GitHub



\### Deployment



\- Microsoft Azure is planned for production hosting.



\---



\## Project Structure



```text

DeepINKCommunity/

│

├── DeepINKCommunity/

│   ├── settings.py

│   ├── urls.py

│   ├── wsgi.py

│   └── \_\_init\_\_.py

│

├── accounts/

│   ├── management/

│   │   └── commands/

│   ├── migrations/

│   ├── templates/

│   │   └── accounts/

│   ├── admin.py

│   ├── forms.py

│   ├── models.py

│   ├── tests.py

│   ├── urls.py

│   └── views.py

│

├── dashboard/

│   ├── migrations/

│   ├── templates/

│   │   └── dashboard/

│   ├── admin.py

│   ├── models.py

│   ├── tests.py

│   ├── urls.py

│   └── views.py

│

├── app/

│   ├── migrations/

│   ├── templates/

│   ├── static/

│   ├── forms.py

│   ├── models.py

│   ├── tests.py

│   └── views.py

│

├── static/

│   └── images/

│       └── deep\_ink\_logo.png

│

├── manage.py

├── requirements.txt

├── .gitignore

└── README.md



\# Deep INK Community Centre



\## Local Development Setup



Follow the steps below to set up the Deep INK Community Centre project on a local development machine.



\### 1. Clone the Repository



Clone the GitHub repository:



```bash

git clone https://github.com/deepinkcom/DeepINKCommunity.git

```



Navigate into the project directory:



```bash

cd DeepINKCommunity

```



\### 2. Create a Virtual Environment

On Windows, create a Python virtual environment:



```bash

python -m venv .venv

```

Activate the virtual environment:



```bash

.venv\\Scripts\\activate

```



After activation, your terminal should show:



```bash

(.venv)

```



\### 3. Install Dependencies

Install the required Python packages:



```bash

pip install -r requirements.txt

```



\### 4. Apply Database Migrations

Apply the existing Django database migrations:



```bash

python manage.py migrate

```



\### 5. Create the User Roles

Create the project roles:



```bash

python manage.py create\_roles

```



The project uses the following roles:

* Administrator
* Manager
* Staff



\### 6. Configure Permissions

Configure the project permissions:



```bash

python manage.py setup\_permissions

```



This configures the custom permissions required by the application, including staff account management permissions.



\### 7. Create an Administrator

Create a Django administrator account:



```bash

python manage.py createsuperuser

```



Follow the prompts to create the Django administrator username, email address and password.



\### 8. Run the Development Server

Start the Django development server:



```bash

python manage.py runserver

```



The application will normally be available at:



```bash

http://127.0.0.1:8000/

```



\## Useful Django Commands

Check the Project

Check for configuration or code issues:



```bash

python manage.py check

```



Apply Migrations



```bash

python manage.py migrate

```



Create Migrations

After making changes to Django models:



```bash

python manage.py makemigrations

```



Run Tests

```bash

python manage.py test

```



Start the Development Server

```bash

python manage.py runserver

```



Create Roles

```bash

python manage.py create\_roles

```



Configure Permissions

```bash

python manage.py setup\_permissions

```



Create an Administrator

```bash

python manage.py createsuperuser

```



\###Environment Variables



Sensitive configuration must not be committed to GitHub.



The Django secret key should be supplied through an environment variable:



```bash

DJANGO\_SECRET\_KEY

```



The project's development settings use:



```bash

SECRET\_KEY = os.environ.get(

&#x20;   'DJANGO\_SECRET\_KEY',

&#x20;   'dev-only-change-this-secret-key'

)

```



The fallback value is intended for local development only.



For production, a secure secret key must be configured through the deployment environment rather than being stored in source control.



Important: Never commit production secret keys, passwords, API keys, access tokens or other credentials to the repository.





\## Important Development Rules

To keep the project secure and prevent conflicts between team members:

1. Do not commit passwords, API keys, secret keys, access tokens or other credentials.

2. Do not commit db.sqlite3.

3. Do not commit virtual environments such as .venv/.

4. Pull the latest changes before beginning team work.

5. Commit changes regularly.

6. Use descriptive Git commit messages.

7. Keep development responsibilities separated according to the team's assigned roles.

8. Do not modify another developer's module unnecessarily.

9. Coordinate changes that affect shared models, URLs or settings before making them.


10\. Run the following command before committing:
```bash
python manage.py check
```



11\. Test your changes locally before pushing them to GitHub.

12\. Do not overwrite or remove another developer's work without discussing the change with the team.

