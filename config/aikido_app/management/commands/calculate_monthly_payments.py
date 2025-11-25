from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Q
from decimal import Decimal
from datetime import datetime
from config.aikido_app.models import (
    PaymentAllocation, ClassSession, InstructorAssignment, 
    ClassType, MonthlyInstructorPayment, MonthlyFederationPayment
)


class Command(BaseCommand):
    help = 'Сарын төлбөрийг тооцоолж багш болон холбоонд хуваарилна (50/50 split, instructor 60/40)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Сарыг YYYY-MM хэлбэрээр оруулна (жишээ: 2025-01)',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Жил (жишээ: 2025)',
        )
        parser.add_argument(
            '--month-number',
            type=int,
            help='Сарын дугаар 1-12 (жишээ: 1 = Нэгдүгээр сар)',
        )
        parser.add_argument(
            '--recalculate',
            action='store_true',
            help='Урьд тооцоолсон мэдээллийг устгаад дахин тооцоолох (АНХААР: Төлөгдсөн цалинг мөн устгана!)',
        )

    def handle(self, *args, **options):
        # Parse month
        if options['month']:
            try:
                year, month = map(int, options['month'].split('-'))
            except ValueError:
                self.stdout.write(self.style.ERROR('Сарын формат буруу байна. YYYY-MM хэлбэрээр оруулна уу'))
                return
        elif options['year'] and options['month_number']:
            year = options['year']
            month = options['month_number']
        else:
            # Default to current month
            now = datetime.now()
            year = now.year
            month = now.month

        # Validate month
        if month < 1 or month > 12:
            self.stdout.write(self.style.ERROR(f'Сарын дугаар 1-12 хооронд байх ёстой: {month}'))
            return

        month_date = datetime(year, month, 1).date()
        self.stdout.write(f'\n📅 Тооцоолж буй сар: {month_date.strftime("%Y-%m")}\n')

        recalculate = options.get('recalculate', False)
        
        # Warning for recalculate mode
        if recalculate:
            self.stdout.write(self.style.WARNING(
                '⚠️  АНХААРУУЛГА: --recalculate горим идэвхтэй байна!'
            ))
            self.stdout.write(self.style.WARNING(
                '    Төлөгдсөн болон банкны гүйлгээтэй холбогдсон цалин мөн дахин тооцоологдоно!\n'
            ))

        # Process each class type
        for class_type in ClassType.objects.all():
            self.stdout.write(f'\n🏫 {class_type.get_name_display()} анги:')
            self.process_class_type(class_type, month_date, recalculate)

        self.stdout.write(self.style.SUCCESS('\n✅ Тооцоолол амжилттай дууслаа!'))

    def process_class_type(self, class_type, month_date, recalculate):
        """Тухайн ангийн төрлийн төлбөрийг тооцоолох"""
        
        # Check if payments already exist and are paid or linked to bank transactions
        existing_payments = MonthlyInstructorPayment.objects.filter(
            class_type=class_type,
            month=month_date
        )
        
        existing_federation = MonthlyFederationPayment.objects.filter(
            class_type=class_type,
            month=month_date
        )
        
        # Check if any payments are already paid or linked to bank transactions
        has_paid_payments = existing_payments.filter(is_paid=True).exists()
        has_linked_payments = existing_payments.filter(bank_transaction__isnull=False).exists()
        has_paid_federation = existing_federation.filter(is_paid=True).exists()
        has_linked_federation = existing_federation.filter(bank_transaction__isnull=False).exists()
        
        if (has_paid_payments or has_linked_payments or has_paid_federation or has_linked_federation) and not recalculate:
            self.stdout.write(self.style.WARNING(
                f'  ⚠️  {month_date.strftime("%Y-%m")} сарын төлбөр аль хэдийн төлөгдсөн эсвэл банкны гүйлгээтэй холбогдсон байна.'
            ))
            self.stdout.write(self.style.WARNING(
                f'      Дахин тооцоолохыг хүсвэл --recalculate flag ашиглана уу.'
            ))
            return
        
        # Get total payments collected for this class type in this month
        payments = PaymentAllocation.objects.filter(
            payment_month__year=month_date.year,
            payment_month__month=month_date.month,
            student__class_types=class_type
        )
        
        total_collected = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        student_count = payments.values('student').distinct().count()
        
        if total_collected == 0:
            self.stdout.write(f'  ⚠️  Төлбөр байхгүй байна')
            return
        
        self.stdout.write(f'  💰 Цуглуулсан төлбөр: {total_collected:,.0f}₮ ({student_count} сурагч)')
        
        # Calculate splits
        instructor_pool = total_collected * Decimal('0.50')  # 50% for instructors
        federation_share = total_collected * Decimal('0.50')  # 50% for federation
        
        self.stdout.write(f'  📊 Багш нарт: {instructor_pool:,.0f}₮ (50%)')
        self.stdout.write(f'  📊 Холбоонд: {federation_share:,.0f}₮ (50%)')
        
        # Save/update federation payment
        if recalculate:
            MonthlyFederationPayment.objects.filter(
                class_type=class_type,
                month=month_date
            ).delete()
        
        federation_payment, created = MonthlyFederationPayment.objects.get_or_create(
            class_type=class_type,
            month=month_date,
            defaults={
                'total_payment_collected': total_collected,
                'federation_share_amount': federation_share,
            }
        )
        
        if not created:
            federation_payment.total_payment_collected = total_collected
            federation_payment.federation_share_amount = federation_share
            federation_payment.save()
        
        # Get all class sessions for this month/class type
        sessions = ClassSession.objects.filter(
            class_type=class_type,
            date__year=month_date.year,
            date__month=month_date.month,
            is_cancelled=False
        )
        
        total_sessions = sessions.count()
        
        if total_sessions == 0:
            self.stdout.write(f'  ⚠️  Хичээл байхгүй байна')
            return
        
        self.stdout.write(f'  📚 Нийт хичээл: {total_sessions}')
        
        # Calculate instructor shares
        # Get lead and assistant instructor counts
        lead_assignments = InstructorAssignment.objects.filter(
            session__in=sessions,
            role=InstructorAssignment.LEAD
        )
        
        assistant_assignments = InstructorAssignment.objects.filter(
            session__in=sessions,
            role=InstructorAssignment.ASSISTANT
        )
        
        # Group by instructor
        lead_instructors = lead_assignments.values('instructor').annotate(
            class_count=Count('id')
        )
        
        assistant_instructors = assistant_assignments.values('instructor').annotate(
            class_count=Count('id')
        )
        
        # Calculate per-assignment payment (NOT per-session)
        # Lead pool (60%) divided by total lead assignments
        # Assistant pool (40%) divided by total assistant assignments
        total_lead_assignments = lead_assignments.count()
        total_assistant_assignments = assistant_assignments.count()
        
        lead_share_per_assignment = (instructor_pool * Decimal('0.60')) / total_lead_assignments if total_lead_assignments > 0 else Decimal('0.00')
        assistant_share_per_assignment = (instructor_pool * Decimal('0.40')) / total_assistant_assignments if total_assistant_assignments > 0 else Decimal('0.00')
        
        self.stdout.write(f'  💵 Ахлах багш (1 хичээл): {lead_share_per_assignment:,.0f}₮ ({total_lead_assignments} assignments)')
        self.stdout.write(f'  💵 Туслах багш (1 хичээл): {assistant_share_per_assignment:,.0f}₮ ({total_assistant_assignments} assignments)')
        
        # Delete old records if recalculating
        if recalculate:
            MonthlyInstructorPayment.objects.filter(
                class_type=class_type,
                month=month_date
            ).delete()
        
        # Save lead instructor payments
        for lead_data in lead_instructors:
            from config.aikido_app.models import Instructor
            instructor = Instructor.objects.get(pk=lead_data['instructor'])
            class_count = lead_data['class_count']
            amount = lead_share_per_assignment * class_count
            
            payment, created = MonthlyInstructorPayment.objects.get_or_create(
                instructor=instructor,
                class_type=class_type,
                month=month_date,
                role=InstructorAssignment.LEAD,
                defaults={
                    'total_classes': class_count,
                    'total_payment_collected': total_collected,
                    'instructor_share_amount': amount,
                }
            )
            
            if not created:
                payment.total_classes = class_count
                payment.total_payment_collected = total_collected
                payment.instructor_share_amount = amount
                payment.save()
            
            self.stdout.write(f'    👨‍🏫 {instructor} (Ахлах): {class_count} хичээл × {lead_share_per_assignment:,.0f}₮ = {amount:,.0f}₮')
        
        # Save assistant instructor payments
        for assistant_data in assistant_instructors:
            from config.aikido_app.models import Instructor
            instructor = Instructor.objects.get(pk=assistant_data['instructor'])
            class_count = assistant_data['class_count']
            amount = assistant_share_per_assignment * class_count
            
            payment, created = MonthlyInstructorPayment.objects.get_or_create(
                instructor=instructor,
                class_type=class_type,
                month=month_date,
                role=InstructorAssignment.ASSISTANT,
                defaults={
                    'total_classes': class_count,
                    'total_payment_collected': total_collected,
                    'instructor_share_amount': amount,
                }
            )
            
            if not created:
                payment.total_classes = class_count
                payment.total_payment_collected = total_collected
                payment.instructor_share_amount = amount
                payment.save()
            
            self.stdout.write(f'    👨‍🏫 {instructor} (Туслах): {class_count} хичээл × {assistant_share_per_assignment:,.0f}₮ = {amount:,.0f}₮')
