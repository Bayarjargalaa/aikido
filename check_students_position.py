import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Student

# Find the students
s1 = Student.objects.filter(first_name__icontains='Соёмбо').first()
s2 = Student.objects.filter(first_name__icontains='Өнөржаргал').first()

if s1:
    print(f'Соёмбо: {s1.first_name} {s1.last_name}')
    print(f'  enrollment_date: {s1.enrollment_date}')
    print(f'  is_active: {s1.is_active}')
    print()

if s2:
    print(f'Өнөржаргал: {s2.first_name} {s2.last_name}')
    print(f'  enrollment_date: {s2.enrollment_date}')
    print(f'  is_active: {s2.is_active}')
    print()

# Check positions in default sort (date_desc)
print("Default sort (date_desc) positions:")
all_students = Student.objects.order_by('-enrollment_date', 'last_name', 'first_name')
for idx, s in enumerate(all_students, 1):
    if 'Соёмбо' in s.first_name or 'Өнөржаргал' in s.first_name:
        page_num = ((idx - 1) // 50) + 1
        print(f'  Position {idx} (Page {page_num}): {s.first_name} {s.last_name}')
