import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import InstructorAssignment, ClassSession, Instructor, ClassType
from datetime import datetime

# Test: Can we assign same instructor as both lead and assistant?
date = datetime(2025, 11, 20).date()
amgalan = Instructor.objects.get(id=1)
morning = ClassType.objects.get(name=ClassType.MORNING)

session, _ = ClassSession.objects.get_or_create(
    date=date,
    defaults={
        'class_type': morning,
        'weekday': date.weekday(),
        'start_time': '09:00',
        'end_time': '11:00',
    }
)

# Clear existing
InstructorAssignment.objects.filter(session=session).delete()

# Try to create both lead and assistant for same instructor
try:
    lead = InstructorAssignment.objects.create(
        session=session,
        instructor=amgalan,
        role='LEAD'
    )
    print(f"✓ Lead created: {lead}")
    
    assistant = InstructorAssignment.objects.create(
        session=session,
        instructor=amgalan,
        role='ASSISTANT'
    )
    print(f"✓ Assistant created: {assistant}")
    
    print("\n✅ SUCCESS! Нэг багш ахлах болон туслах хоёуланд нь томилогдож чадна.")
    
except Exception as e:
    print(f"❌ ERROR: {e}")

# Check all assignments for this session
assignments = InstructorAssignment.objects.filter(session=session)
print(f"\nНийт томилолт: {assignments.count()}")
for a in assignments:
    print(f"  - {a.instructor.last_name}: {a.get_role_display()}")
