from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Student(models.Model):
    """Сурагч - Айкидо сургалтад хамрагдагчид"""
    
    # Rank choices
    KYU_CHOICES = [
        (1, '1 кюү'),
        (2, '2 кюү'),
        (3, '3 кюү'),
        (4, '4 кюү'),
        (5, '5 кюү'),
        (6, '6 кюү'),
        (7, '7 кюү'),
        (8, '8 кюү'),
    ]
    
    DAN_CHOICES = [
        (1, '1 дан'),
        (2, '2 дан'),
        (3, '3 дан'),
        (4, '4 дан'),
        (5, '5 дан'),
        (6, '6 дан'),
        (7, '7 дан'),
        (8, '8 дан'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='student_profile',
        verbose_name="Хэрэглэгч"
    )
    first_name = models.CharField(max_length=100, verbose_name="Нэр")
    last_name = models.CharField(max_length=100, verbose_name="Овог")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Утас")
    email = models.EmailField(blank=True, verbose_name="И-мэйл")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Төрсөн огноо")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Элссэн огноо")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй эсэх")
    kyu_rank = models.IntegerField(
        choices=KYU_CHOICES,
        null=True,
        blank=True,
        verbose_name="Кюү зэрэг"
    )
    dan_rank = models.IntegerField(
        choices=DAN_CHOICES,
        null=True,
        blank=True,
        verbose_name="Дан зэрэг"
    )
    current_rank_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Одоогийн зэрэг авсан огноо"
    )
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Сарын төлбөр"
    )
    fee_note = models.TextField(
        blank=True,
        verbose_name="Төлбөрийн тайлбар"
    )
    class_types = models.ManyToManyField(
        'ClassType',
        blank=True,
        verbose_name="Элссэн ангиуд"
    )
    
    class Meta:
        verbose_name = "Сурагч"
        verbose_name_plural = "Сурагчид"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_rank_display_full(self):
        """Зэрэг цолыг бүтнээр харуулах"""
        if self.dan_rank:
            return f"{self.get_dan_rank_display()}"
        elif self.kyu_rank:
            return f"{self.get_kyu_rank_display()}"
        return "Зэрэггүй"
    
    def save(self, *args, **kwargs):
        """Override save to track rank history"""
        # Check if this is an existing record (has pk)
        if self.pk:
            try:
                # Get the old version from database
                old_instance = Student.objects.get(pk=self.pk)
                
                # Check if rank changed
                rank_changed = (
                    old_instance.kyu_rank != self.kyu_rank or 
                    old_instance.dan_rank != self.dan_rank
                )
                
                # If rank changed and there was a previous rank, save to history
                if rank_changed and (old_instance.kyu_rank or old_instance.dan_rank):
                    from .models import RankHistory
                    RankHistory.objects.create(
                        student=self,
                        rank_type='kyu' if old_instance.kyu_rank else 'dan',
                        rank_number=old_instance.kyu_rank or old_instance.dan_rank,
                        obtained_date=old_instance.current_rank_date or old_instance.enrollment_date,
                        notes=f'Автоматаар хадгалагдсан: {old_instance.get_rank_display_full()}'
                    )
            except Student.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)


class Instructor(models.Model):
    """Багш - Хичээл заадаг багш нар"""
    
    # Rank choices
    KYU_CHOICES = [
        (1, '1 кюү'),
        (2, '2 кюү'),
        (3, '3 кюү'),
        (4, '4 кюү'),
        (5, '5 кюү'),
        (6, '6 кюү'),
        (7, '7 кюү'),
        (8, '8 кюү'),
    ]
    
    DAN_CHOICES = [
        (1, '1 дан'),
        (2, '2 дан'),
        (3, '3 дан'),
        (4, '4 дан'),
        (5, '5 дан'),
        (6, '6 дан'),
        (7, '7 дан'),
        (8, '8 дан'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='instructor_profile',
        verbose_name="Хэрэглэгч"
    )
    first_name = models.CharField(max_length=100, verbose_name="Нэр")
    last_name = models.CharField(max_length=100, verbose_name="Овог")
    phone = models.CharField(max_length=20, verbose_name="Утас")
    email = models.EmailField(blank=True, verbose_name="И-мэйл")
    hire_date = models.DateField(verbose_name="Ажилд орсон огноо")
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй эсэх")
    kyu_rank = models.IntegerField(
        choices=KYU_CHOICES,
        null=True,
        blank=True,
        verbose_name="Кюү зэрэг"
    )
    dan_rank = models.IntegerField(
        choices=DAN_CHOICES,
        null=True,
        blank=True,
        verbose_name="Дан зэрэг"
    )
    current_rank_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Одоогийн зэрэг авсан огноо"
    )
    
    class Meta:
        verbose_name = "Багш"
        verbose_name_plural = "Багш нар"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_rank_display_full(self):
        """Зэрэг цолыг бүтнээр харуулах"""
        if self.dan_rank:
            return f"{self.get_dan_rank_display()}"
        elif self.kyu_rank:
            return f"{self.get_kyu_rank_display()}"
        return "Зэрэггүй"
    
    def save(self, *args, **kwargs):
        """Override save to track rank history"""
        # Check if this is an existing record (has pk)
        if self.pk:
            try:
                # Get the old version from database
                old_instance = Instructor.objects.get(pk=self.pk)
                
                # Check if rank changed
                rank_changed = (
                    old_instance.kyu_rank != self.kyu_rank or 
                    old_instance.dan_rank != self.dan_rank
                )
                
                # If rank changed and there was a previous rank, save to history
                if rank_changed and (old_instance.kyu_rank or old_instance.dan_rank):
                    from .models import RankHistory
                    RankHistory.objects.create(
                        instructor=self,
                        rank_type='kyu' if old_instance.kyu_rank else 'dan',
                        rank_number=old_instance.kyu_rank or old_instance.dan_rank,
                        obtained_date=old_instance.current_rank_date or old_instance.hire_date,
                        notes=f'Автоматаар хадгалагдсан: {old_instance.get_rank_display_full()}'
                    )
            except Instructor.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)


class ClassType(models.Model):
    """Ангийн төрөл - Өглөө, Орой, Хүүхэд"""
    MORNING = 'MORNING'
    EVENING = 'EVENING'
    CHILDREN = 'CHILDREN'
    
    CLASS_TYPE_CHOICES = [
        (MORNING, 'Өглөө'),
        (EVENING, 'Орой'),
        (CHILDREN, 'Хүүхэд'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=CLASS_TYPE_CHOICES,
        unique=True,
        verbose_name="Ангийн төрөл"
    )
    description = models.TextField(blank=True, verbose_name="Тайлбар")
    
    class Meta:
        verbose_name = "Ангийн төрөл"
        verbose_name_plural = "Ангийн төрлүүд"
    
    def __str__(self):
        return self.get_name_display()


class ClassSession(models.Model):
    """Хичээлийн хуваарь - Тодорхой өдрийн хичээл"""
    MONDAY = 1
    WEDNESDAY = 3
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 0
    
    WEEKDAY_CHOICES = [
        (MONDAY, 'Даваа'),
        (WEDNESDAY, 'Лхагва'),
        (FRIDAY, 'Баасан'),
        (SATURDAY, 'Бямба'),
        (SUNDAY, 'Ням'),
    ]
    
    class_type = models.ForeignKey(
        ClassType,
        on_delete=models.CASCADE,
        verbose_name="Ангийн төрөл"
    )
    date = models.DateField(verbose_name="Огноо")
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name="Гараг"
    )
    start_time = models.TimeField(verbose_name="Эхлэх цаг")
    end_time = models.TimeField(verbose_name="Дуусах цаг")
    notes = models.TextField(blank=True, verbose_name="Тэмдэглэл")
    is_cancelled = models.BooleanField(default=False, verbose_name="Хичээл ороогүй эсэх")
    
    class Meta:
        verbose_name = "Хичээлийн хуваарь"
        verbose_name_plural = "Хичээлийн хуваарь"
        ordering = ['-date', 'start_time']
    
    def __str__(self):
        return f"{self.class_type} - {self.date} ({self.get_weekday_display()})"


class InstructorAssignment(models.Model):
    """Багшийн томилолт - Хичээлд томилогдсон багш нар"""
    LEAD = 'LEAD'
    ASSISTANT = 'ASSISTANT'
    
    ROLE_CHOICES = [
        (LEAD, 'Ахлах багш'),
        (ASSISTANT, 'Туслах багш'),
    ]
    
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='instructor_assignments',
        verbose_name="Хичээл"
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        verbose_name="Багш"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="Үүрэг"
    )
    
    class Meta:
        verbose_name = "Багшийн томилолт"
        verbose_name_plural = "Багшийн томилолтууд"
        unique_together = ['session', 'instructor', 'role']
    
    def __str__(self):
        return f"{self.instructor} - {self.get_role_display()} ({self.session.date})"


class Attendance(models.Model):
    """Ирц - Сурагчдын ирц"""
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Хичээл"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Сурагч"
    )
    is_present = models.BooleanField(default=True, verbose_name="Ирсэн эсэх")
    recorded_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Бүртгэсэн багш"
    )
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Бүртгэсэн цаг")
    notes = models.TextField(blank=True, verbose_name="Тэмдэглэл")
    
    class Meta:
        verbose_name = "Ирц"
        verbose_name_plural = "Ирц"
        unique_together = ['session', 'student']
        ordering = ['-session__date']
    
    def __str__(self):
        status = "Ирсэн" if self.is_present else "Тасалсан"
        return f"{self.student} - {self.session.date} ({status})"


class Payment(models.Model):
    """Төлбөр - Сурагчдын төлбөрийн бүртгэл"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Сурагч"
    )
    transaction_date = models.DateField(verbose_name="Гүйлгээний огноо")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Дүн"
    )
    description = models.TextField(verbose_name="Тайлбар")
    payment_month = models.DateField(
        null=True,
        blank=True,
        verbose_name="Төлбөрийн сар"
    )
    bank_reference = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Банкны лавлагаа"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Баталгаажсан эсэх"
    )
    # Link to bank transaction if imported
    bank_transaction = models.ForeignKey(
        'BankTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_payments',
        verbose_name="Банкны гүйлгээ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Шинэчилсэн огноо")
    
    class Meta:
        verbose_name = "Төлбөр"
        verbose_name_plural = "Төлбөрүүд"
        ordering = ['-transaction_date']
    
    def __str__(self):
        student_name = self.student if self.student else "Тодорхойгүй"
        return f"{student_name} - {self.amount}₮ ({self.transaction_date})"


class RankHistory(models.Model):
    """Зэрэг цолын түүх - Сурагч болон багшийн зэрэг цолын өөрчлөлтийг хадгална"""
    
    RANK_TYPE_CHOICES = [
        ('kyu', 'Кюү'),
        ('dan', 'Дан'),
    ]
    
    # Student or Instructor (one of them will be filled)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rank_history',
        verbose_name="Сурагч"
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rank_history',
        verbose_name="Багш"
    )
    
    rank_type = models.CharField(
        max_length=10,
        choices=RANK_TYPE_CHOICES,
        verbose_name="Зэрэг төрөл"
    )
    rank_number = models.IntegerField(
        verbose_name="Зэрэг дугаар"
    )
    obtained_date = models.DateField(
        verbose_name="Авсан огноо"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Бүртгэсэн огноо"
    )
    
    class Meta:
        verbose_name = "Зэрэг цолын түүх"
        verbose_name_plural = "Зэрэг цолын түүхүүд"
        ordering = ['-obtained_date']
    
    def __str__(self):
        person = self.student or self.instructor
        rank_display = f"{self.rank_number} {self.get_rank_type_display()}"
        return f"{person} - {rank_display} ({self.obtained_date})"


class BankTransaction(models.Model):
    """Банкны гүйлгээний бичлэг - Excel файлаас импортлосон"""
    
    STATUS_PENDING = 'PENDING'
    STATUS_MATCHED = 'MATCHED'
    STATUS_PARTIALLY_MATCHED = 'PARTIALLY_MATCHED'
    STATUS_IGNORED = 'IGNORED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Хүлээгдэж буй'),
        (STATUS_MATCHED, 'Холбогдсон'),
        (STATUS_PARTIALLY_MATCHED, 'Хэсэгчлэн холбогдсон'),
        (STATUS_IGNORED, 'Орхигдсон'),
    ]
    
    transaction_date = models.DateField(verbose_name="Гүйлгээний огноо")
    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Эхний үлдэгдэл"
    )
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Дебит гүйлгээ"
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Кредит гүйлгээ"
    )
    closing_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Эцсийн үлдэгдэл"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Дүн (кредит)",
        help_text="Кредит гүйлгээний дүн"
    )
    description = models.TextField(verbose_name="Гүйлгээний утга")
    counterparty_account = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Харьцсан данс"
    )
    reference_number = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Лавлагааны дугаар"
    )
    payer_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Төлөгчийн нэр"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Төлөв"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name="Импортлосон огноо")
    
    class Meta:
        verbose_name = "Банкны гүйлгээ"
        verbose_name_plural = "Банкны гүйлгээнүүд"
        ordering = ['-transaction_date', '-imported_at']
    
    def __str__(self):
        return f"{self.transaction_date} - {self.amount}₮ - {self.payer_name or 'Тодорхойгүй'}"
    
    def get_allocated_amount(self):
        """Хуваарилагдсан нийт дүн (орлого эсвэл зардал)"""
        # Кредит гүйлгээ бол PaymentAllocation болон IncomeAllocation-оос
        if self.credit_amount and self.credit_amount > 0:
            payment_total = self.allocations.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            income_total = self.income_allocations.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            seminar_total = self.seminar_allocations.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            membership_total = self.membership_allocations.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            return payment_total + income_total + seminar_total + membership_total
        # Дебит гүйлгээ бол ExpenseAllocation-оос
        elif self.debit_amount and self.debit_amount != 0:
            return self.expense_allocations.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        return Decimal('0.00')
    
    def get_remaining_amount(self):
        """Үлдсэн дүн"""
        return self.amount - self.get_allocated_amount()
    
    def update_status(self):
        """Төлөвийг автоматаар шинэчлэх"""
        allocated = self.get_allocated_amount()
        if allocated == Decimal('0.00'):
            self.status = self.STATUS_PENDING
        elif allocated >= self.amount:
            self.status = self.STATUS_MATCHED
        else:
            self.status = self.STATUS_PARTIALLY_MATCHED
        self.save()


class PaymentAllocation(models.Model):
    """Төлбөрийн хуваарилалт - Банкны гүйлгээг сурагч + сартай холбох"""
    
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name="Банкны гүйлгээ"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='payment_allocations',
        verbose_name="Сурагч"
    )
    payment_month = models.DateField(verbose_name="Төлбөрийн сар")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Дүн"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    created_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Үүсгэсэн хэрэглэгч"
    )
    
    class Meta:
        verbose_name = "Төлбөрийн хуваарилалт"
        verbose_name_plural = "Төлбөрийн хуваарилалтууд"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.payment_month.strftime('%Y-%m')} - {self.amount}₮"


class IncomeCategory(models.Model):
    """Орлогын төрөл/ангилал (сарын төлбөрөөс бусад орлого)"""
    
    CATEGORY_CHOICES = [
        ('SEMINAR', 'Семинарын хураамж'),
        ('MEMBERSHIP', 'Гишүүнчлэлийн хураамж'),
        ('EXAM', 'Шалгалтын хураамж'),
        ('EVENT', 'Арга хэмжээний орлого'),
        ('MERCHANDISE', 'Бараа борлуулалт'),
        ('OTHER', 'Бусад орлого'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Нэр"
    )
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER',
        verbose_name="Төрөл"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Тайлбар"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    
    class Meta:
        verbose_name = "Орлогын ангилал"
        verbose_name_plural = "Орлогын ангиллууд"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class IncomeAllocation(models.Model):
    """Орлогын хуваарилалт - Банкны гүйлгээг орлогын ангилалтай холбох"""
    
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='income_allocations',
        verbose_name="Банкны гүйлгээ"
    )
    income_category = models.ForeignKey(
        IncomeCategory,
        on_delete=models.PROTECT,
        verbose_name="Орлогын ангилал"
    )
    income_date = models.DateField(verbose_name="Орлогын огноо")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Дүн"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    created_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Үүсгэсэн хэрэглэгч"
    )
    
    class Meta:
        verbose_name = "Орлогын хуваарилалт"
        verbose_name_plural = "Орлогын хуваарилалтууд"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.income_category} - {self.income_date} - {self.amount}₮"


class Seminar(models.Model):
    """Семинар/Арга хэмжээ"""
    
    name = models.CharField(
        max_length=200,
        verbose_name="Нэр"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Тайлбар"
    )
    seminar_date = models.DateField(verbose_name="Семинарын огноо")
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Төлбөр",
        help_text="Нэг хүний төлбөр"
    )
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй эсэх")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    
    class Meta:
        verbose_name = "Семинар"
        verbose_name_plural = "Семинарууд"
        ordering = ['-seminar_date']
    
    def __str__(self):
        return f"{self.name} ({self.seminar_date})"


class SeminarPaymentAllocation(models.Model):
    """Семинарын төлбөрийн хуваарилалт - Банкны гүйлгээг сурагч + семинартай холбох"""
    
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='seminar_allocations',
        verbose_name="Банкны гүйлгээ"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Сурагч"
    )
    seminar = models.ForeignKey(
        Seminar,
        on_delete=models.PROTECT,
        verbose_name="Семинар"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Төлсөн дүн"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    created_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Үүсгэсэн хэрэглэгч"
    )
    
    class Meta:
        verbose_name = "Семинарын төлбөр"
        verbose_name_plural = "Семинарын төлбөрүүд"
        ordering = ['-created_at']
        unique_together = ['student', 'seminar']  # Нэг семинарт нэг удаа төлнө
    
    def __str__(self):
        return f"{self.student} - {self.seminar} - {self.amount}₮"


class MembershipPaymentAllocation(models.Model):
    """Гишүүнчлэлийн төлбөрийн хуваарилалт - Банкны гүйлгээг сурагч + сартай холбох"""
    
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='membership_allocations',
        verbose_name="Банкны гүйлгээ"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Сурагч"
    )
    payment_month = models.DateField(
        verbose_name="Төлбөрийн сар",
        help_text="Аль сарын гишүүнчлэлийн төлбөр"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Төлсөн дүн"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    created_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Үүсгэсэн хэрэглэгч"
    )
    
    class Meta:
        verbose_name = "Гишүүнчлэлийн төлбөр"
        verbose_name_plural = "Гишүүнчлэлийн төлбөрүүд"
        ordering = ['-payment_month', '-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.payment_month.strftime('%Y-%m')} - {self.amount}₮"


class ExpenseCategory(models.Model):
    """Зардлын төрөл/ангилал"""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Нэр"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Тайлбар"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    
    class Meta:
        verbose_name = "Зардлын ангилал"
        verbose_name_plural = "Зардлын ангиллууд"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ExpenseAllocation(models.Model):
    """Зардлын хуваарилалт - Банкны гүйлгээг зардлын ангилалтай холбох"""
    
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='expense_allocations',
        verbose_name="Банкны гүйлгээ"
    )
    expense_category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='allocations',
        verbose_name="Зардлын ангилал"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Дүн"
    )
    expense_date = models.DateField(
        verbose_name="Зардлын огноо",
        help_text="Зардал гарсан огноо"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    created_by = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Үүсгэсэн хэрэглэгч"
    )
    
    class Meta:
        verbose_name = "Зардлын хуваарилалт"
        verbose_name_plural = "Зардлын хуваарилалтууд"
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.expense_category} - {self.expense_date} - {self.amount}₮"


class MonthlyInstructorPayment(models.Model):
    """Багшийн сарын төлбөр - Хичээл заасны төлбөр (сарын төлбөрийн 50%-ийн 60% ахлах, 40% туслах)"""
    
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='monthly_payments',
        verbose_name="Багш"
    )
    class_type = models.ForeignKey(
        ClassType,
        on_delete=models.CASCADE,
        verbose_name="Ангийн төрөл"
    )
    month = models.DateField(
        verbose_name="Сар",
        help_text="Тухайн сарын эхний өдөр"
    )
    role = models.CharField(
        max_length=20,
        choices=InstructorAssignment.ROLE_CHOICES,
        verbose_name="Үүрэг"
    )
    total_classes = models.IntegerField(
        default=0,
        verbose_name="Нийт хичээлийн тоо",
        help_text="Тухайн сард заасан хичээлийн тоо"
    )
    total_payment_collected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Цуглуулсан нийт төлбөр",
        help_text="Энэ ангийн сурагчдаас цуглуулсан сарын төлбөрийн нийт дүн"
    )
    instructor_share_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Багшийн хувь",
        help_text="Багшид олгох төлбөр (50%-ийн 60% эсвэл 40%)"
    )
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructor_payments',
        verbose_name="Банкны гүйлгээ",
        help_text="Төлбөр олгосон банкны гүйлгээ"
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Олгосон эсэх"
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Олгосон огноо"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Шинэчилсэн огноо")
    
    class Meta:
        verbose_name = "Багшийн сарын төлбөр"
        verbose_name_plural = "Багшийн сарын төлбөрүүд"
        ordering = ['-month', 'class_type', 'instructor']
        unique_together = ['instructor', 'class_type', 'month', 'role']
    
    def __str__(self):
        return f"{self.instructor} - {self.class_type} - {self.month.strftime('%Y-%m')} - {self.get_role_display()} - {self.instructor_share_amount}₮"


class MonthlyFederationPayment(models.Model):
    """Холбооны сарын төлбөр - Монголын айкидогийн холбоонд өгөх (сарын төлбөрийн 50%)"""
    
    class_type = models.ForeignKey(
        ClassType,
        on_delete=models.CASCADE,
        verbose_name="Ангийн төрөл"
    )
    month = models.DateField(
        verbose_name="Сар",
        help_text="Тухайн сарын эхний өдөр"
    )
    total_payment_collected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Цуглуулсан нийт төлбөр",
        help_text="Энэ ангийн сурагчдаас цуглуулсан сарын төлбөрийн нийт дүн"
    )
    federation_share_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Холбооны хувь",
        help_text="Холбоонд олгох төлбөр (50%)"
    )
    bank_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='federation_payments',
        verbose_name="Банкны гүйлгээ",
        help_text="Төлбөр олгосон банкны гүйлгээ"
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Олгосон эсэх"
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Олгосон огноо"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Тэмдэглэл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Шинэчилсэн огноо")
    
    class Meta:
        verbose_name = "Холбооны сарын төлбөр"
        verbose_name_plural = "Холбооны сарын төлбөрүүд"
        ordering = ['-month', 'class_type']
        unique_together = ['class_type', 'month']
    
    def __str__(self):
        return f"{self.class_type} - {self.month.strftime('%Y-%m')} - {self.federation_share_amount}₮"
