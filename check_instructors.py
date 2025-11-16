import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Instructor

print("=== Багш нарын жагсаалт ===")
print(f"Нийт багш: {Instructor.objects.count()}")
print()

for instructor in Instructor.objects.all():
    print(f"{instructor.id}: {instructor.last_name} {instructor.first_name}")
    print(f"   Утас: {instructor.phone}")
    print(f"   Идэвхтэй: {instructor.is_active}")
    print()
