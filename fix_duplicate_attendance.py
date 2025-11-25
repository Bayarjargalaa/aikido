"""
Fix duplicate attendance records where students in EVENING class 
were incorrectly recorded in MORNING class sessions
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Student, Attendance, ClassType, ClassSession
from datetime import datetime

# Find students mentioned: Жаргал Баясгалан and Отгонбаяр Баяржаргал
students = Student.objects.filter(
    last_name__icontains='Жаргал'
) | Student.objects.filter(
    last_name__icontains='Баяржаргал'
)

morning_type = ClassType.objects.get(name='MORNING')
evening_type = ClassType.objects.get(name='EVENING')

with open('fix_duplicate_attendance_report.txt', 'w', encoding='utf-8') as f:
    f.write("Duplicate Attendance Check\n")
    f.write("=" * 80 + "\n\n")
    
    for student in students:
        f.write(f"\nStudent: {student.first_name} {student.last_name} (ID: {student.id})\n")
        
        # Check student's class types
        student_class_types = student.class_types.all()
        f.write(f"  Registered class types: {[ct.get_name_display() for ct in student_class_types]}\n")
        
        # Get all attendance records
        all_attendance = Attendance.objects.filter(student=student).select_related('session', 'session__class_type')
        
        # Count by class type
        morning_count = all_attendance.filter(session__class_type=morning_type).count()
        evening_count = all_attendance.filter(session__class_type=evening_type).count()
        
        f.write(f"  Total attendance: {all_attendance.count()}\n")
        f.write(f"    - MORNING: {morning_count}\n")
        f.write(f"    - EVENING: {evening_count}\n")
        
        # If student is only registered for EVENING but has MORNING attendance
        if evening_type in student_class_types and morning_type not in student_class_types:
            if morning_count > 0:
                f.write(f"\n  ⚠️  PROBLEM: Student is EVENING-only but has {morning_count} MORNING attendance records!\n")
                
                # Get the wrong attendance records
                wrong_attendance = all_attendance.filter(session__class_type=morning_type)
                
                f.write(f"  Wrong MORNING attendance records:\n")
                for att in wrong_attendance.order_by('-session__date')[:20]:
                    f.write(f"    - {att.session.date}: Session ID {att.session.id}, ")
                    f.write(f"Recorded by: {att.recorded_by}, ")
                    f.write(f"Created: {att.created_at}\n")
                
                # Delete them
                deleted_count = wrong_attendance.delete()[0]
                f.write(f"\n  ✓ Deleted {deleted_count} wrong MORNING attendance records!\n")
        
        # If student is only registered for MORNING but has EVENING attendance
        elif morning_type in student_class_types and evening_type not in student_class_types:
            if evening_count > 0:
                f.write(f"\n  ⚠️  PROBLEM: Student is MORNING-only but has {evening_count} EVENING attendance records!\n")
                
                wrong_attendance = all_attendance.filter(session__class_type=evening_type)
                
                f.write(f"  Wrong EVENING attendance records:\n")
                for att in wrong_attendance.order_by('-session__date')[:20]:
                    f.write(f"    - {att.session.date}: Session ID {att.session.id}, ")
                    f.write(f"Recorded by: {att.recorded_by}, ")
                    f.write(f"Created: {att.created_at}\n")
                
                deleted_count = wrong_attendance.delete()[0]
                f.write(f"\n  ✓ Deleted {deleted_count} wrong EVENING attendance records!\n")

print("Report saved to fix_duplicate_attendance_report.txt")
