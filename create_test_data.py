import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import InstructorAssignment, ClassSession, Instructor, ClassType
from datetime import datetime
import calendar

print("=== 2025 оны 11-р сарын календар ===")

year = 2025
month = 11

# Get all weekdays
cal = calendar.monthcalendar(year, month)
print(f"\n{year} оны {month} сар:")
print("Да Мя Лх Пү Ба Бя Ня")
for week in cal:
    print(" ".join(f"{day:2}" if day > 0 else "  " for day in week))

print("\n=== Монdays (Даваа) ===")
mondays = [datetime(year, month, day) for week in cal for day in week if day > 0 and datetime(year, month, day).weekday() == 0]
for date in mondays:
    print(f"  {date.date()}")

print("\n=== Wednesdays (Лхагва) ===")
wednesdays = [datetime(year, month, day) for week in cal for day in week if day > 0 and datetime(year, month, day).weekday() == 2]
for date in wednesdays:
    print(f"  {date.date()}")

print("\n=== Saturdays (Бямба) ===")
saturdays = [datetime(year, month, day) for week in cal for day in week if day > 0 and datetime(year, month, day).weekday() == 5]
for date in saturdays:
    print(f"  {date.date()}")

print("\n=== Одоо тест өгөгдөл үүсгэж байна ===")

# Get instructors
amgalan = Instructor.objects.get(id=1)
bayasgalan = Instructor.objects.get(id=2)
galbaa = Instructor.objects.get(id=3)

# Get class types
morning = ClassType.objects.get(name=ClassType.MORNING)
evening = ClassType.objects.get(name=ClassType.EVENING)
children = ClassType.objects.get(name=ClassType.CHILDREN)

count = 0

# Mondays - Morning
for date_obj in mondays:
    date = date_obj.date()
    session, _ = ClassSession.objects.get_or_create(
        date=date,
        defaults={
            'class_type': morning,
            'weekday': 0,
            'start_time': '09:00',
            'end_time': '11:00',
        }
    )
    session.class_type = morning
    session.save()
    
    InstructorAssignment.objects.get_or_create(
        session=session,
        instructor=amgalan,
        defaults={'role': 'LEAD'}
    )
    count += 1
    print(f"✓ {date} Өглөө - {amgalan.last_name} (Ахлах)")

# Wednesdays - Evening
for date_obj in wednesdays:
    date = date_obj.date()
    session, _ = ClassSession.objects.get_or_create(
        date=date,
        defaults={
            'class_type': evening,
            'weekday': 2,
            'start_time': '18:00',
            'end_time': '20:00',
        }
    )
    session.class_type = evening
    session.save()
    
    InstructorAssignment.objects.get_or_create(
        session=session,
        instructor=bayasgalan,
        defaults={'role': 'LEAD'}
    )
    InstructorAssignment.objects.get_or_create(
        session=session,
        instructor=amgalan,
        defaults={'role': 'ASSISTANT'}
    )
    count += 2
    print(f"✓ {date} Орой - {bayasgalan.last_name} (Ахлах), {amgalan.last_name} (Туслах)")

# Saturdays - Children
for date_obj in saturdays:
    date = date_obj.date()
    session, _ = ClassSession.objects.get_or_create(
        date=date,
        defaults={
            'class_type': children,
            'weekday': 5,
            'start_time': '10:00',
            'end_time': '12:00',
        }
    )
    session.class_type = children
    session.save()
    
    InstructorAssignment.objects.get_or_create(
        session=session,
        instructor=galbaa,
        defaults={'role': 'LEAD'}
    )
    count += 1
    print(f"✓ {date} Хүүхэд - {galbaa.last_name} (Ахлах)")

print(f"\n=== {count} томилолт үүсгэлээ! ===")
print("\nОдоо: http://127.0.0.1:8000/attendance/record/?class_type=MORNING&month=2025-11")
