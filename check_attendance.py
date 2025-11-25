#!/usr/bin/env python
"""Check Дугар Амгаланбаяр attendance in 2025"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Student, Attendance
from datetime import date

# Find student
student = Student.objects.get(
    first_name__icontains='Амгаланбаяр',
    last_name__icontains='Дугар'
)

print("=" * 80)
print(f"ATTENDANCE CHECK FOR: {student}")
print("=" * 80)

# Get attendance for 2025
attendances = Attendance.objects.filter(
    student=student,
    session__date__year=2025,
    is_present=True
).select_related('session').order_by('session__date')

if attendances.exists():
    print(f"\nTotal attendance records in 2025: {attendances.count()}")
    
    # Group by month
    from collections import defaultdict
    by_month = defaultdict(int)
    
    for att in attendances:
        month_key = date(att.session.date.year, att.session.date.month, 1)
        by_month[month_key] += 1
    
    print("\nAttendance by month:")
    for month, count in sorted(by_month.items()):
        print(f"  {month.strftime('%Y-%m')}: {count} sessions")
    
    print("\nFirst 10 attendance records:")
    for att in attendances[:10]:
        print(f"  {att.session.date} ({att.session.class_type.name}): Present")
else:
    print("\n❌ NO ATTENDANCE RECORDS found for 2025!")
    print("\nThis is why 'Чөлөөлөгдсөн' badge is not showing.")
    print("The badge only shows when:")
    print("  1. Student is fee exempt (✓ TRUE)")
    print("  2. Student has attendance in that month (✗ FALSE)")
