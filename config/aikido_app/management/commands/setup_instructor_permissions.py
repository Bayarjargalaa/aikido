"""
Management command to set up instructor permissions based on their names
"""
from django.core.management.base import BaseCommand
from config.aikido_app.models import Instructor, ClassType


class Command(BaseCommand):
    help = 'Set up instructor allowed_class_types based on their names'

    def handle(self, *args, **options):
        # Get class types
        morning = ClassType.objects.get(name='MORNING')
        evening = ClassType.objects.get(name='EVENING')
        children = ClassType.objects.get(name='CHILDREN')
        
        # Get all instructors
        instructors = Instructor.objects.filter(is_active=True)
        
        for inst in instructors:
            name_lower = (inst.first_name + inst.last_name).lower()
            
            # Clear existing permissions
            inst.allowed_class_types.clear()
            
            # Set permissions based on name
            if 'амгалан' in name_lower:
                inst.allowed_class_types.add(morning)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {inst.first_name} {inst.last_name} → Өглөөний анги')
                )
            elif 'баясгалан' in name_lower or 'баясгал' in name_lower:
                inst.allowed_class_types.add(evening)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {inst.first_name} {inst.last_name} → Оройн анги')
                )
            elif 'галбадрах' in name_lower or 'галба' in name_lower:
                inst.allowed_class_types.add(children)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {inst.first_name} {inst.last_name} → Хүүхдийн анги')
                )
            else:
                # Leave unrestricted (no allowed_class_types = can teach all)
                self.stdout.write(
                    self.style.WARNING(f'○ {inst.first_name} {inst.last_name} → Хязгаарлалтгүй (бүх анги)')
                )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Багш нарын эрх амжилттай тохируулагдлаа!'))
