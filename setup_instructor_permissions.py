import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.aikido_app.models import Instructor, ClassType

print("=== Багш нарын эрх тохируулж байна ===\n")

# Get class types
try:
    morning = ClassType.objects.get(name=ClassType.MORNING)
    evening = ClassType.objects.get(name=ClassType.EVENING)
    children = ClassType.objects.get(name=ClassType.CHILDREN)
    print("✓ Ангиудыг олсон:")
    print(f"  - Өглөөний анги: {morning}")
    print(f"  - Оройн анги: {evening}")
    print(f"  - Хүүхдийн анги: {children}\n")
except ClassType.DoesNotExist as e:
    print(f"❌ Алдаа: Ангийн төрөл олдсонгүй - {e}")
    exit(1)

# Setup Галбадрах - хүүхдийн анги
try:
    galbaa = Instructor.objects.get(first_name__icontains="Галбадрах")
    galbaa.allowed_class_types.clear()
    galbaa.allowed_class_types.add(children)
    print(f"✓ {galbaa} - Хүүхдийн ангийн төлбөр харна")
except Instructor.DoesNotExist:
    print("⚠️  Галбадрах багш олдсонгүй")

# Setup Амгаланбаяр - өглөөний анги
try:
    amgalan = Instructor.objects.get(first_name__icontains="Амгаланбаяр")
    amgalan.allowed_class_types.clear()
    amgalan.allowed_class_types.add(morning)
    print(f"✓ {amgalan} - Өглөөний ангийн төлбөр харна")
except Instructor.DoesNotExist:
    print("⚠️  Амгаланбаяр багш олдсонгүй")

# Setup Баясгалан - бүх анги
try:
    bayasgalan = Instructor.objects.get(first_name__icontains="Баясгалан")
    bayasgalan.allowed_class_types.clear()
    # Хоосон үлдээвэл бүх ангийг харна (эсвэл бүгдийг нэмж болно)
    # Энд бүх ангийг нэмье
    bayasgalan.allowed_class_types.add(morning, evening, children)
    print(f"✓ {bayasgalan} - Бүх ангийн төлбөр харна")
except Instructor.DoesNotExist:
    print("⚠️  Баясгалан багш олдсонгүй")

print("\n✅ Тохиргоо амжилттай дууслаа!")
print("\nБагш нарын эрхийн дэлгэрэнгүй:")
for instructor in Instructor.objects.all():
    allowed = instructor.allowed_class_types.all()
    if allowed.exists():
        class_list = ", ".join([ct.get_name_display() for ct in allowed])
        print(f"  {instructor}: {class_list}")
    else:
        print(f"  {instructor}: Бүх анги")
