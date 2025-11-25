"""
Delete attendance records for wrong weekdays:
- MORNING/EVENING classes on Sat/Sun (5,6)
- CHILDREN classes on Mon/Wed/Fri (0,2,4)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Attendance, ClassType

morning = ClassType.objects.get(name='MORNING')
evening = ClassType.objects.get(name='EVENING')
children = ClassType.objects.get(name='CHILDREN')

with open('delete_wrong_weekday_attendance.txt', 'w', encoding='utf-8') as f:
    f.write("Delete Wrong Weekday Attendance Records\n")
    f.write("=" * 80 + "\n\n")
    
    # Find MORNING/EVENING attendance on Sat/Sun (5, 6)
    wrong_morning_evening = Attendance.objects.filter(
        session__class_type__in=[morning, evening],
        session__date__week_day__in=[1, 7]  # Django week_day: 1=Sun, 7=Sat
    ).select_related('session', 'session__class_type', 'student')
    
    f.write(f"MORNING/EVENING attendance on Sat/Sun: {wrong_morning_evening.count()}\n\n")
    
    if wrong_morning_evening.exists():
        for att in wrong_morning_evening[:50]:
            weekday_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][att.session.date.weekday()]
            f.write(f"  - {att.student.first_name} {att.student.last_name}: ")
            f.write(f"{att.session.class_type.get_name_display()} on {att.session.date} ({weekday_name})\n")
        
        deleted = wrong_morning_evening.delete()[0]
        f.write(f"\n✓ Deleted {deleted} wrong MORNING/EVENING attendance records on weekends\n")
    
    # Find CHILDREN attendance on Mon/Wed/Fri (0, 2, 4)
    wrong_children = Attendance.objects.filter(
        session__class_type=children,
        session__date__week_day__in=[2, 4, 6]  # Django week_day: 2=Mon, 4=Wed, 6=Fri
    ).select_related('session', 'session__class_type', 'student')
    
    f.write(f"\n\nCHILDREN attendance on Mon/Wed/Fri: {wrong_children.count()}\n\n")
    
    if wrong_children.exists():
        for att in wrong_children[:50]:
            weekday_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][att.session.date.weekday()]
            f.write(f"  - {att.student.first_name} {att.student.last_name}: ")
            f.write(f"{att.session.class_type.get_name_display()} on {att.session.date} ({weekday_name})\n")
        
        deleted = wrong_children.delete()[0]
        f.write(f"\n✓ Deleted {deleted} wrong CHILDREN attendance records on weekdays\n")

print("Report saved to delete_wrong_weekday_attendance.txt")
