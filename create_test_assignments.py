import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import InstructorAssignment, ClassSession, Instructor, ClassType
from datetime import datetime, timedelta

print("=== Тест өгөгдөл үүсгэж байна ===")

# Get instructors
amgalan = Instructor.objects.get(id=1)  # Амгаланбаяр
bayasgalan = Instructor.objects.get(id=2)  # Баясгалан
galbaa = Instructor.objects.get(id=3)  # Галбадрах

# Get class types
morning = ClassType.objects.get(name=ClassType.MORNING)
evening = ClassType.objects.get(name=ClassType.EVENING)
children = ClassType.objects.get(name=ClassType.CHILDREN)

# Create some sessions and assignments for this month
today = datetime.now().date()
year = today.year
month = today.month

# Generate test data for this month
created_count = 0

# Monday - Morning class (Amgalanbaatar)
for week in range(1, 5):
    day = (week - 1) * 7 + 1  # 1, 8, 15, 22
    try:
        date = datetime(year, month, day).date()
        if date.weekday() == 0:  # Monday
            session, created = ClassSession.objects.get_or_create(
                date=date,
                class_type=morning,
                defaults={
                    'weekday': 0,
                    'start_time': '09:00',
                    'end_time': '11:00',
                }
            )
            if created or not session.instructor_assignments.exists():
                InstructorAssignment.objects.get_or_create(
                    session=session,
                    instructor=amgalan,
                    role='LEAD'
                )
                created_count += 1
                print(f"✓ Өглөө: {date} - {amgalan.last_name} (Ахлах)")
    except:
        pass

# Wednesday - Evening class (Bayasgalan)
for week in range(1, 5):
    day = (week - 1) * 7 + 3  # 3, 10, 17, 24
    try:
        date = datetime(year, month, day).date()
        if date.weekday() == 2:  # Wednesday
            session, created = ClassSession.objects.get_or_create(
                date=date,
                class_type=evening,
                defaults={
                    'weekday': 2,
                    'start_time': '18:00',
                    'end_time': '20:00',
                }
            )
            if created or not session.instructor_assignments.exists():
                InstructorAssignment.objects.get_or_create(
                    session=session,
                    instructor=bayasgalan,
                    role='LEAD'
                )
                InstructorAssignment.objects.get_or_create(
                    session=session,
                    instructor=amgalan,
                    role='ASSISTANT'
                )
                created_count += 2
                print(f"✓ Орой: {date} - {bayasgalan.last_name} (Ахлах), {amgalan.last_name} (Туслах)")
    except:
        pass

# Saturday - Children class (Galbaa)
for week in range(1, 5):
    day = (week - 1) * 7 + 6  # 6, 13, 20, 27
    try:
        date = datetime(year, month, day).date()
        if date.weekday() == 5:  # Saturday
            session, created = ClassSession.objects.get_or_create(
                date=date,
                class_type=children,
                defaults={
                    'weekday': 5,
                    'start_time': '10:00',
                    'end_time': '12:00',
                }
            )
            if created or not session.instructor_assignments.exists():
                InstructorAssignment.objects.get_or_create(
                    session=session,
                    instructor=galbaa,
                    role='LEAD'
                )
                created_count += 1
                print(f"✓ Хүүхэд: {date} - {galbaa.last_name} (Ахлах)")
    except:
        pass

print()
print(f"=== Нийт {created_count} томилолт үүсгэлээ ===")
print()
print("Одоо http://127.0.0.1:8000/attendance/record/ хуудсанд орж шалгана уу!")
