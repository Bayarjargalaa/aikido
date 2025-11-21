import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Instructor, MonthlyInstructorPayment, ClassType
from datetime import datetime

print("=== Багш нарын төлбөрийн эрх тест ===\n")

# Test each instructor's view permissions
for instructor in Instructor.objects.filter(is_active=True):
    print(f"\n{'='*60}")
    print(f"Багш: {instructor}")
    print(f"{'='*60}")
    
    allowed_class_types = instructor.allowed_class_types.all()
    
    if allowed_class_types.exists():
        print(f"Харах эрхтэй ангиуд: {', '.join([ct.get_name_display() for ct in allowed_class_types])}")
    else:
        print("Харах эрхтэй ангиуд: Бүх анги")
    
    # Simulate what this instructor would see
    payments = MonthlyInstructorPayment.objects.filter(instructor=instructor)
    
    # Filter by allowed class types if set
    if allowed_class_types.exists():
        payments = payments.filter(class_type__in=allowed_class_types)
    
    print(f"\nХарах боломжтой төлбөрүүд:")
    if payments.exists():
        for payment in payments.select_related('class_type'):
            print(f"  - {payment.class_type.get_name_display()}: {payment.month.strftime('%Y-%m')} - {payment.instructor_share_amount}₮ ({payment.get_role_display()})")
    else:
        print("  (Төлбөр алга)")

print(f"\n{'='*60}")
print("✅ Тест дууслаа!")
print(f"{'='*60}")
