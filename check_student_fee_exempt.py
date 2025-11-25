#!/usr/bin/env python
"""Check if Дугар Амгаланбаяр is fee exempt"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Student
from django.db.models import Q

# Find student
students = Student.objects.filter(
    first_name__icontains='Амгаланбаяр',
    last_name__icontains='Дугар'
)

print("=" * 80)
print("SEARCHING FOR: Дугар Амгаланбаяр")
print("=" * 80)

if students.exists():
    for student in students:
        print(f"\nStudent found: {student}")
        print(f"  ID: {student.id}")
        print(f"  Full Name: {student.last_name} {student.first_name}")
        print(f"  Phone: {student.phone}")
        print(f"  Monthly Fee: {student.monthly_fee}₮")
        print(f"  is_fee_exempt: {student.is_fee_exempt}")
        print(f"  Fee Note: {student.fee_note}")
        print(f"  Is Active: {student.is_active}")
        print(f"  Classes: {', '.join([ct.name for ct in student.class_types.all()])}")
        print("-" * 80)
        
        if not student.is_fee_exempt:
            print("\n⚠️  WARNING: Student is NOT marked as fee exempt!")
            print("To mark as fee exempt, go to admin or edit student form and check the checkbox.")
else:
    print("\n❌ No student found with name 'Дугар Амгаланбаяр'")
    print("\nSearching all students with similar names...")
    
    # Try variations
    similar = Student.objects.filter(
        Q(first_name__icontains='Амгалан') | 
        Q(last_name__icontains='Дугар')
    )
    
    if similar.exists():
        print(f"\nFound {similar.count()} similar students:")
        for s in similar:
            print(f"  - {s.last_name} {s.first_name} (ID: {s.id})")
