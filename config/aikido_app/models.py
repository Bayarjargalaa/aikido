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
