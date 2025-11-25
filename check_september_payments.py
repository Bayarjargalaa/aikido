#!/usr/bin/env python
"""Check September instructor payments calculation"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import MonthlyInstructorPayment, ClassType
from datetime import date

# Check September 2025 payments
payments = MonthlyInstructorPayment.objects.filter(
    month=date(2025, 9, 1)
).order_by('instructor__first_name', 'class_type__name', 'role')

print("September 2025 Instructor Payments:")
print("=" * 100)

for payment in payments:
    print(f"\nInstructor: {payment.instructor.first_name} {payment.instructor.last_name}")
    print(f"Class Type: {payment.class_type.get_name_display()}")
    print(f"Role: {payment.get_role_display()}")
    print(f"Total Classes: {payment.total_classes}")
    print(f"Payment per Class: {payment.payment_per_class:,.2f}₮")
    print(f"Instructor Share: {payment.instructor_share_amount:,.2f}₮")
    
    # Calculate what it should be
    if payment.payment_per_class and payment.total_classes:
        calculated = payment.payment_per_class * payment.total_classes
        print(f"Calculation: {payment.payment_per_class:,.2f}₮ × {payment.total_classes} = {calculated:,.2f}₮")
        
        if abs(calculated - payment.instructor_share_amount) > 0.01:
            print(f"⚠️  MISMATCH! Expected {calculated:,.2f}₮ but got {payment.instructor_share_amount:,.2f}₮")
    
    print("-" * 100)

# Show example with 13077
print("\n\nSearching for payments with 13077₮ per class:")
print("=" * 100)
payments_13077 = MonthlyInstructorPayment.objects.filter(
    month=date(2025, 9, 1),
    payment_per_class=13077
)

for payment in payments_13077:
    print(f"\nInstructor: {payment.instructor.first_name} {payment.instructor.last_name}")
    print(f"Class Type: {payment.class_type.get_name_display()}")
    print(f"Role: {payment.get_role_display()}")
    print(f"Total Classes: {payment.total_classes}")
    print(f"Payment per Class: {payment.payment_per_class:,.0f}₮")
    print(f"Instructor Share: {payment.instructor_share_amount:,.0f}₮")
    print(f"Expected: {payment.payment_per_class * payment.total_classes:,.0f}₮")
    print(f"Difference: {(payment.payment_per_class * payment.total_classes) - payment.instructor_share_amount:,.0f}₮")
