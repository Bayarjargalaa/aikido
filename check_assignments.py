import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import InstructorAssignment, ClassSession
from datetime import datetime

print("=== Багш томилолтын статистик ===")
print(f"Нийт хичээл: {ClassSession.objects.count()}")
print(f"Нийт багш томилолт: {InstructorAssignment.objects.count()}")
print()

if InstructorAssignment.objects.exists():
    print("Багш томилолтууд:")
    for assignment in InstructorAssignment.objects.select_related('instructor', 'session').order_by('-session__date')[:10]:
        print(f"  {assignment.session.date} - {assignment.instructor.last_name} {assignment.instructor.first_name} ({assignment.get_role_display()})")
else:
    print("Багш томилолт байхгүй байна!")
    print()
    print("Ирц бүртгэх хуудсанд орж багш нарыг сонгоход л статистик харагдана.")
