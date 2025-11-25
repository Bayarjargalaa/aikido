#!/usr/bin/env python
"""Analyze September payment calculation details"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import (
    MonthlyInstructorPayment, MonthlyFederationPayment,
    PaymentAllocation, ClassSession, InstructorAssignment, ClassType
)
from datetime import date
from decimal import Decimal

month_date = date(2025, 9, 1)

print("=" * 100)
print("SEPTEMBER 2025 PAYMENT CALCULATION ANALYSIS")
print("=" * 100)

for class_type in ClassType.objects.all():
    print(f"\n{'='*100}")
    print(f"CLASS TYPE: {class_type.get_name_display()}")
    print(f"{'='*100}")
    
    # Get payments collected
    payments = PaymentAllocation.objects.filter(
        payment_month__year=2025,
        payment_month__month=9,
        student__class_types=class_type
    )
    
    total_collected = sum(p.amount for p in payments)
    student_count = payments.values('student').distinct().count()
    
    print(f"\n1. COLLECTED PAYMENTS:")
    print(f"   Total Collected: {total_collected:,.0f}₮")
    print(f"   Students: {student_count}")
    
    if total_collected == 0:
        print("   ⚠️  No payments - skipping\n")
        continue
    
    # Calculate splits
    instructor_pool = total_collected * Decimal('0.50')
    federation_share = total_collected * Decimal('0.50')
    
    print(f"\n2. 50/50 SPLIT:")
    print(f"   Instructor Pool (50%): {instructor_pool:,.2f}₮")
    print(f"   Federation Share (50%): {federation_share:,.2f}₮")
    
    # Get sessions
    sessions = ClassSession.objects.filter(
        class_type=class_type,
        date__year=2025,
        date__month=9,
        is_cancelled=False
    )
    
    total_sessions = sessions.count()
    print(f"\n3. SESSIONS:")
    print(f"   Total Sessions: {total_sessions}")
    
    if total_sessions == 0:
        print("   ⚠️  No sessions - skipping\n")
        continue
    
    # Get assignments
    lead_assignments = InstructorAssignment.objects.filter(
        session__in=sessions,
        role=InstructorAssignment.LEAD
    )
    
    assistant_assignments = InstructorAssignment.objects.filter(
        session__in=sessions,
        role=InstructorAssignment.ASSISTANT
    )
    
    total_lead = lead_assignments.count()
    total_assistant = assistant_assignments.count()
    
    print(f"   Lead Assignments: {total_lead}")
    print(f"   Assistant Assignments: {total_assistant}")
    
    # Calculate per-class rates
    lead_pool = instructor_pool * Decimal('0.60')
    assistant_pool = instructor_pool * Decimal('0.40')
    
    lead_per_class = lead_pool / total_sessions if total_sessions > 0 else Decimal('0')
    assistant_per_class = assistant_pool / total_sessions if total_sessions > 0 else Decimal('0')
    
    print(f"\n4. PER-CLASS CALCULATION:")
    print(f"   Lead Pool (60% of instructor pool): {lead_pool:,.2f}₮")
    print(f"   Lead Per Class: {lead_pool:,.2f}₮ / {total_sessions} = {lead_per_class:,.2f}₮")
    print(f"   ")
    print(f"   Assistant Pool (40% of instructor pool): {assistant_pool:,.2f}₮")
    print(f"   Assistant Per Class: {assistant_pool:,.2f}₮ / {total_sessions} = {assistant_per_class:,.2f}₮")
    
    # Show actual payments in database
    print(f"\n5. ACTUAL DATABASE PAYMENTS:")
    db_payments = MonthlyInstructorPayment.objects.filter(
        class_type=class_type,
        month=month_date
    ).order_by('instructor__first_name', 'role')
    
    for payment in db_payments:
        calculated = Decimal(str(payment.total_classes)) * (
            lead_per_class if payment.role == InstructorAssignment.LEAD else assistant_per_class
        )
        
        role_name = "LEAD" if payment.role == InstructorAssignment.LEAD else "ASST"
        per_class = lead_per_class if payment.role == InstructorAssignment.LEAD else assistant_per_class
        
        print(f"\n   {payment.instructor.first_name} {payment.instructor.last_name} ({role_name}):")
        print(f"      Classes: {payment.total_classes}")
        print(f"      Per Class: {per_class:,.2f}₮")
        print(f"      Expected: {per_class:,.2f}₮ × {payment.total_classes} = {calculated:,.2f}₮")
        print(f"      Database: {payment.instructor_share_amount:,.2f}₮")
        
        diff = payment.instructor_share_amount - calculated
        if abs(diff) > Decimal('0.01'):
            print(f"      ⚠️  MISMATCH: {diff:+,.2f}₮")
        else:
            print(f"      ✓ Match")
    
    # Check if 13077 appears
    if any(abs(p.instructor_share_amount / p.total_classes - Decimal('13077')) < 1 for p in db_payments if p.total_classes > 0):
        print(f"\n   🔍 FOUND 13077₮ per class in this class type!")

print("\n" + "=" * 100)
