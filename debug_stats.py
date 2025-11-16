import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import InstructorAssignment, ClassSession, Instructor, ClassType
from datetime import datetime
import calendar

year = 2025
month = 11

# Get class types
morning = ClassType.objects.get(name=ClassType.MORNING)

print("=== 2025-11 сарын ӨГЛӨӨНИЙ ангийн мэдээлэл ===\n")

# Get dates for morning classes (Mon, Wed, Fri)
cal = calendar.monthcalendar(year, month)
target_weekdays = [0, 2, 4]  # Monday, Wednesday, Friday
dates = []
for week in cal:
    for day in week:
        if day > 0:
            date = datetime(year, month, day).date()
            if date.weekday() in target_weekdays:
                dates.append(date)

print(f"Өглөөний ангийн огноонууд ({len(dates)})")
for date in dates:
    print(f"  {date}")

print("\n=== ClassSession records ===")
sessions = ClassSession.objects.filter(date__in=dates)
print(f"Нийт session: {sessions.count()}")
for session in sessions:
    print(f"  {session.date} - {session.class_type.get_name_display()} (class_type.name={session.class_type.name})")

print("\n=== InstructorAssignment дэлгэрэнгүй ===")
assignments = InstructorAssignment.objects.filter(
    session__date__in=dates
).select_related('instructor', 'session', 'session__class_type')

print(f"Нийт assignment: {assignments.count()}")
for assignment in assignments:
    print(f"  {assignment.session.date} - {assignment.instructor.last_name} ({assignment.get_role_display()}) - Class: {assignment.session.class_type.name}")

print("\n=== Өглөөний ангийн статистик ===")
for instructor in Instructor.objects.all():
    lead_count = InstructorAssignment.objects.filter(
        instructor=instructor,
        role='LEAD',
        session__date__in=dates,
        session__class_type__name=ClassType.MORNING
    ).count()
    
    assistant_count = InstructorAssignment.objects.filter(
        instructor=instructor,
        role='ASSISTANT',
        session__date__in=dates,
        session__class_type__name=ClassType.MORNING
    ).count()
    
    if lead_count > 0 or assistant_count > 0:
        print(f"{instructor.last_name} {instructor.first_name}: Ахлах={lead_count}, Туслах={assistant_count}")
