# Aikido Django Project - AI Coding Agent Instructions

## Project Overview

An **Aikido training center management system** for tracking students, instructors, classes, attendance, and payments.

### Business Domain

- **Classes**: Morning, Evening, and Children's classes
- **Instructors**: Can teach multiple class types; registered as either Lead or Assistant for each session
- **Students**: Enroll in classes and attend sessions
- **Attendance**: Instructors record attendance for their students
- **Payments**: Track student payment records

## Project Architecture

This is a **Django 5.2.8** project with a non-standard structure where the project configuration lives in `config/` (not the typical project root).

### Key Structural Decisions

- **Project root**: `config/` contains Django settings, URLs, WSGI/ASGI configurations
- **Django apps**: Located as subdirectories within `config/` (e.g., `config/aikido_app/`)
- **Virtual environment**: `aikido_venv/` at project root (included in repo - atypical but intentional)
- **Database**: SQLite3 at project root (`db.sqlite3`)

### App Registration Pattern

Apps MUST be registered with their full Python path in `config/settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'config.aikido_app',  # NOT just 'aikido_app'
]
```

Apps are configured in their `apps.py` with the full path:
```python
class AikidoAppConfig(AppConfig):
    name = 'config.aikido_app'  # Match the INSTALLED_APPS entry
```

## Developer Workflows

### Environment Setup

```powershell
# Activate virtual environment (Windows PowerShell)
.\aikido_venv\Scripts\Activate.ps1

# Install dependencies (if requirements.txt exists)
pip install -r requirements.txt
```

### Running the Development Server

```powershell
python manage.py runserver
```

### Database Migrations

```powershell
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Admin Interface

Access Django admin at `http://localhost:8000/admin/` after creating a superuser:
```powershell
python manage.py createsuperuser
```

## Project Conventions

### File Locations

- **Settings**: `config/settings.py`
- **Root URLs**: `config/urls.py`
- **App code**: `config/<app_name>/` (models, views, admin, tests)
- **Management commands**: Run from project root using `manage.py`

### Current State

- Single app: `config.aikido_app` contains all business logic
- SQLite database for development
- Django 5.2.8 with default middleware stack
- Admin interface is primary UI (no custom frontend yet)

### Domain Models (to be implemented in `config/aikido_app/models.py`)

```python
# Core entities:
- Student: Training participants (can enroll in multiple classes)
- Instructor: Teachers (can be lead or assistant)
- ClassType: Morning, Evening, Children's (enum/choices)
- ClassSession: Specific class instances with date/time
  - Morning/Evening: Mon, Wed, Fri
  - Children's: Sat, Sun
- InstructorAssignment: Links instructors to sessions (role: lead/assistant)
- Attendance: Student presence records per session
- Payment: Student payment transactions
  - Imported from bank statements
  - Linked to student + month manually
  - Tracks amount paid per month
```

### Business Rules

1. **Instructors** can teach multiple class types (Morning, Evening, Children's)
2. **Each class session** has one or more instructors with specific roles:
   - **Lead Instructor** (ахлах багш): Primary teacher
   - **Assistant Instructor** (туслах багш): Supporting teacher
3. **Attendance** is recorded by instructors for their students per session
4. **Students** can enroll in multiple class types simultaneously
5. **Class Schedule**:
   - Morning & Evening classes: Monday, Wednesday, Friday
   - Children's classes: Saturday, Sunday
6. **Payment Processing**:
   - Payments imported from bank statements (CSV/Excel)
   - Bank data includes: transaction date, amount, description
   - Admin manually links payments to student + month
   - System displays total paid amount per student per month

### When Adding New Apps

1. Create app inside `config/`: `python manage.py startapp <app_name> config/<app_name>`
2. Update `apps.py` with full path: `name = 'config.<app_name>'`
3. Register in `INSTALLED_APPS` with full path: `'config.<app_name>'`

## Critical Notes

- This project uses PowerShell on Windows - use `;` for command chaining, not `&&`
- Virtual environment is tracked in repo (non-standard) - assume it's available
- No custom static/media file configuration yet (uses Django defaults)
- DEBUG mode is ON - do not deploy as-is
