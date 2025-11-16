from django.core.management.base import BaseCommand
from config.aikido_app.models import ClassType


class Command(BaseCommand):
    help = 'Үндсэн ангийн төрлүүдийг үүсгэх'

    def handle(self, *args, **options):
        # Check if class types already exist
        if ClassType.objects.exists():
            self.stdout.write(self.style.WARNING('Ангийн төрлүүд аль хэдийн байна'))
            return

        class_types = [
            {
                'name': 'Өглөө',
                'type': ClassType.MORNING,
                'description': 'Өглөөний анги - Даваа, Лхагва, Баасан 07:00-08:30'
            },
            {
                'name': 'Орой',
                'type': ClassType.EVENING,
                'description': 'Оройн анги - Даваа, Лхагва, Баасан 19:00-20:30'
            },
            {
                'name': 'Хүүхдийн',
                'type': ClassType.CHILDREN,
                'description': 'Хүүхдийн анги - Бямба, Ням 10:00-11:30'
            },
        ]

        for ct_data in class_types:
            class_type = ClassType.objects.create(**ct_data)
            self.stdout.write(
                self.style.SUCCESS(f'Амжилттай үүсгэлээ: {class_type.name}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Нийт {len(class_types)} ангийн төрөл үүсгэгдлээ!')
        )
