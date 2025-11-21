# Aikido Django Project - AI Coding Agent Instructions

## Project Overview

**Aikido training center management system** for tracking students, instructors, classes, attendance, and financial operations.

### Business Domain

- **Classes**: Morning/Evening (Mon/Wed/Fri), Children's (Sat/Sun)
- **Instructors**: Lead/Assistant roles, kyu/dan rank tracking with history
- **Students**: Multiple class enrollment, rank progression, custom monthly fees
- **Attendance**: Session-based presence tracking
- **Financial System**: Bank statement import → manual allocation workflow

## Architecture & Structure

**Django 5.2.8** with non-standard `config/` project root (NOT Django default).

### Critical File Locations

```
config/
├── settings.py, urls.py, wsgi.py, asgi.py  # Django core
└── aikido_app/                             # Single app contains all logic
    ├── models.py                           # 19 models (1015 lines)
    ├── views.py                            # 50+ views (2310 lines)
    ├── admin.py                            # Django admin configs
    ├── urls.py                             # App-level routes
    ├── backends.py                         # Email authentication
    ├── forms.py                            # Bank upload forms
    ├── templates/aikido_app/               # 23 templates
    ├── templatetags/custom_filters.py      # Custom template filters
    └── management/commands/
        ├── create_class_types.py           # Init ClassType data
        └── calculate_monthly_payments.py   # Calculate instructor/federation payments
```

### App Registration Pattern (MANDATORY)

Apps MUST use full Python path in `INSTALLED_APPS`:
```python
INSTALLED_APPS = ['config.aikido_app']  # NOT 'aikido_app'
```

Match in `apps.py`:
```python
class AikidoAppConfig(AppConfig):
    name = 'config.aikido_app'
```

## Domain Models (19 models in `models.py`)

### Core Entities
- **Student/Instructor**: `user` (OneToOne), rank fields (`kyu_rank`/`dan_rank`), `current_rank_date`
- **ClassType**: 3 choices (MORNING/EVENING/CHILDREN)
- **ClassSession**: `date`, `weekday`, `start_time`, `end_time`, `is_cancelled`
- **InstructorAssignment**: Links instructor to session with role (LEAD/ASSISTANT)
  - `unique_together = ['session', 'instructor', 'role']` prevents duplicates
- **Attendance**: `session` + `student` + `is_present`, `recorded_by` instructor

### Financial Models (10 models - complex workflow)
1. **BankTransaction**: Imported from Excel (openpyxl)
   - Fields: `transaction_date`, `credit_amount`, `debit_amount`, `description`, `payer_name`
   - `status`: PENDING → MATCHED/PARTIALLY_MATCHED based on allocations
   - Methods: `get_allocated_amount()`, `get_remaining_amount()`, `update_status()`

2. **Allocation Models** (link bank transactions to categories):
   - `PaymentAllocation`: Student monthly tuition (student + payment_month + amount)
   - `SeminarPaymentAllocation`: Event fees (student + seminar + amount, unique together)
   - `MembershipPaymentAllocation`: Membership fees (student + payment_month + amount)
   - `IncomeAllocation`: Other income (income_category + income_date + amount)
   - `ExpenseAllocation`: Expenses (expense_category + expense_date + amount)

3. **Payment Distribution Models** (NEW):
   - `MonthlyInstructorPayment`: Tracks instructor monthly earnings
     - 50% of collected tuition goes to instructors
     - Split: Lead 60%, Assistant 40% (of instructor pool)
     - Fields: `instructor`, `class_type`, `month`, `role`, `total_classes`, `instructor_share_amount`, `is_paid`
   - `MonthlyFederationPayment`: Tracks federation share
     - 50% of collected tuition goes to Mongolian Aikido Federation
     - Fields: `class_type`, `month`, `total_payment_collected`, `federation_share_amount`, `is_paid`

4. **Category Models**:
   - `IncomeCategory`: SEMINAR/MEMBERSHIP/EXAM/EVENT/MERCHANDISE/OTHER
   - `ExpenseCategory`: Free-form expense types
   - `Seminar`: Event tracking (name, seminar_date, fee)

5. **RankHistory**: Tracks rank changes for Student/Instructor
   - Auto-created in `save()` override when rank changes

### Key Model Patterns

**Rank Display**:
```python
def get_rank_display_full(self):
    if self.dan_rank:
        return f"{self.get_dan_rank_display()}"  # "1 дан"
    elif self.kyu_rank:
        return f"{self.get_kyu_rank_display()}"  # "1 кюү"
    return "Зэрэггүй"
```

**Auto Status Updates**: BankTransaction status changes when allocations added/removed via `update_status()`.

## Financial Workflow (Critical Implementation)

### Bank Statement Import Flow
1. **Upload** (`bank_transaction_upload`): Excel file → parse with openpyxl → create BankTransaction records
2. **Match** (`bank_transaction_match`): 
   - GET: Display transaction + allocation forms (student payments, seminars, membership, income, expenses)
   - POST: Create allocation records based on `income_type` parameter:
     - `student_payment` → PaymentAllocation
     - `seminar_payment` → SeminarPaymentAllocation
     - `membership_payment` → MembershipPaymentAllocation
     - `other_income` → IncomeAllocation
     - `expense` → ExpenseAllocation
   - Call `transaction.update_status()` after each allocation
   - Redirect to same page if remaining amount > 0
3. **Delete Allocations**: Individual delete views for each allocation type

### Views Architecture (`views.py` - 2310 lines)

**Authentication**: Custom `EmailBackend` in `backends.py` (email OR username login)
- `LOGIN_REDIRECT_URL = 'dashboard'`, `LOGIN_URL = 'login'`

**Key Views**:
- `dashboard`: Stats + week's classes + recent transactions
- CRUD views for students, instructors (with rank history inlines)
- `class_schedule`: Session management with instructor assignments
- `attendance_record`: Mark attendance + auto-create session if missing
- `bank_transaction_list/upload/match`: Financial workflow
- Payment list views: `payment_list`, `seminar_payment_list`, `membership_payment_list`, `income_list`
- **Payment Distribution Views** (NEW):
  - `monthly_payment_report`: Overview dashboard with 50/50 split visualization
  - `instructor_payment_list`: Filterable list of instructor payments with mark-as-paid action
  - `federation_payment_list`: Filterable list of federation payments with mark-as-paid action
  - `mark_instructor_payment_paid` / `mark_federation_payment_paid`: POST endpoints to mark payments as paid

**URL Pattern**: All routes in `config/aikido_app/urls.py`, included in `config/urls.py` as `path('', include('config.aikido_app.urls'))`

## Developer Workflows

### PowerShell Commands (Windows-specific)
```powershell
# Virtual env (tracked in repo at aikido_venv/)
.\aikido_venv\Scripts\Activate.ps1

# Migrations after model changes
python manage.py makemigrations ; python manage.py migrate

# Run server (default: http://localhost:8000)
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Initialize class types
python manage.py create_class_types

# Calculate monthly payment distributions (NEW)
python manage.py calculate_monthly_payments --month 2025-01
python manage.py calculate_monthly_payments --year 2025 --month-number 1
python manage.py calculate_monthly_payments  # Current month
python manage.py calculate_monthly_payments --month 2025-01 --recalculate  # Force recalculation
```

**IMPORTANT**: Use `;` for command chaining (NOT `&&` in PowerShell).

### Dependencies (requirements.txt)
- Django==5.2.8
- openpyxl==3.1.5 (Excel parsing for bank statements)
- sqlparse, asgiref, tzdata

### Database: SQLite3 (`db.sqlite3` at project root)

## UI & Templates

**Admin Interface**: Primary UI at `/admin/` (19 ModelAdmin classes in `admin.py`)
- Inlines: RankHistoryInline for Student/Instructor
- Custom fieldsets with Mongolian labels

**Custom Templates**: 23 HTML files in `config/aikido_app/templates/aikido_app/`
- `base.html`: Bootstrap-based layout
- Complex forms: `bank_transaction_match.html` (600+ lines with JavaScript for dynamic allocation rows)
- CRUD templates: `student_form.html`, `instructor_form.html`
- Payment reports: `monthly_payment_report.html`, `instructor_payment_list.html`, `federation_payment_list.html`

**Template Tags**: `custom_filters.py` for custom Jinja2 filters

## Critical Business Rules

1. **Rank Changes**: Auto-tracked in RankHistory via `save()` override
2. **Instructor Assignment**: Cannot duplicate (session + instructor + role) via `unique_together`
3. **Seminar Payment**: One payment per student per seminar (`unique_together`)
4. **Bank Transaction Status**: Auto-calculated from allocation totals
5. **Student Monthly Fees**: Variable per student (`monthly_fee` field + `fee_note`)
6. **Class Schedules**: Fixed days per type (Morning/Evening: Mon/Wed/Fri; Children: Sat/Sun)
7. **Payment Distribution** (NEW - CRITICAL):
   - **50/50 Split**: Total collected tuition split equally between Federation (50%) and Instructors (50%)
   - **Instructor Split**: Of the instructor pool (50% of total):
     - Lead Instructor: 60% (per class taught)
     - Assistant Instructor: 40% (per class taught)
   - Calculation: Run `calculate_monthly_payments` management command after allocating bank transactions
   - Payment per class = (Total Collected × 50% × Role%) / Total Classes in Month

## Adding New Features

### New Model
1. Add to `models.py` with verbose_name (Mongolian)
2. Create migration: `python manage.py makemigrations`
3. Apply: `python manage.py migrate`
4. Register in `admin.py` with ModelAdmin class
5. Add to `views.py` if CRUD needed
6. Update templates

### New Allocation Type (Financial)
1. Create model inheriting allocation pattern (see `PaymentAllocation`)
2. Add to `BankTransaction.get_allocated_amount()` aggregation
3. Update `bank_transaction_match` view POST logic
4. Add form fields to `bank_transaction_match.html`
5. Create delete view + URL pattern

## Known Issues & Gotchas

- Virtual environment tracked in repo (non-standard) - don't `.gitignore` it
- DEBUG=True in settings - do NOT deploy as-is
- No static file collection configured (uses Django defaults)
- Templates use Mongolian text extensively (UTF-8 required)
- Large view functions (2310 lines) - consider refactoring for new features
- No REST API - all operations via Django templates

## Documentation Files

- `БУСАД_ОРЛОГО_ТАЙЛБАР.md`: Detailed explanation of "other income" feature implementation (Mongolian)
- Test scripts: `check_*.py`, `create_test_*.py`, `debug_stats.py` (utility scripts, not production code)
