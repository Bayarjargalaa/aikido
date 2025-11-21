import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import MonthlyInstructorPayment, InstructorPaymentAllocation
from decimal import Decimal

print("=== Багшийн төлбөрийн хэсэгчлэн төлөх систем тест ===\n")

# Get a sample instructor payment
payments = MonthlyInstructorPayment.objects.all()[:3]

for payment in payments:
    print(f"\n{'='*60}")
    print(f"Багш: {payment.instructor}")
    print(f"Анги: {payment.class_type.get_name_display()}")
    print(f"Сар: {payment.month.strftime('%Y-%m')}")
    print(f"Үүрэг: {payment.get_role_display()}")
    print(f"{'='*60}")
    
    print(f"\nТөлбөрийн мэдээлэл:")
    print(f"  Нийт төлбөр: {payment.instructor_share_amount:,.0f}₮")
    print(f"  Төлсөн дүн: {payment.paid_amount:,.0f}₮")
    print(f"  Үлдсэн дүн: {payment.get_remaining_amount():,.0f}₮")
    print(f"  Төлөв: {payment.get_payment_status()}")
    print(f"  Төлөгдсөн эсэх: {'Тийм' if payment.is_paid else 'Үгүй'}")
    
    # Show allocations if any
    allocations = payment.allocations.all()
    if allocations.exists():
        print(f"\n  Хуваарилалтууд ({allocations.count()}):")
        for alloc in allocations:
            print(f"    - {alloc.amount:,.0f}₮ (Банк гүйлгээ #{alloc.bank_transaction.id}, {alloc.created_at.strftime('%Y-%m-%d')})")
            if alloc.notes:
                print(f"      Тайлбар: {alloc.notes}")
    else:
        print(f"\n  Хуваарилалт: Алга")

print(f"\n\n{'='*60}")
print("✅ Тест дууслаа!")
print(f"{'='*60}\n")

# Show summary
total_payments = MonthlyInstructorPayment.objects.count()
paid_payments = MonthlyInstructorPayment.objects.filter(is_paid=True).count()
partially_paid = MonthlyInstructorPayment.objects.filter(
    paid_amount__gt=0, 
    paid_amount__lt=django.db.models.F('instructor_share_amount')
).count()

print(f"Нийт багшийн төлбөр: {total_payments}")
print(f"Бүрэн төлөгдсөн: {paid_payments}")
print(f"Хэсэгчлэн төлөгдсөн: {partially_paid}")
print(f"Огт төлөгдөөгүй: {total_payments - paid_payments}")
