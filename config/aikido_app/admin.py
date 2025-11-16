from django.contrib import admin
from .models import (
    Student, Instructor, ClassType, ClassSession, InstructorAssignment, 
    Attendance, Payment, RankHistory, BankTransaction, PaymentAllocation,
    ExpenseCategory, ExpenseAllocation
)


class RankHistoryInline(admin.TabularInline):
    model = RankHistory
    extra = 1
    fields = ['rank_type', 'rank_number', 'obtained_date', 'notes']
    ordering = ['-obtained_date']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'get_rank', 'monthly_fee', 'current_rank_date', 'enrollment_date', 'is_active']
    list_filter = ['is_active', 'enrollment_date', 'kyu_rank', 'dan_rank']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering = ['last_name', 'first_name']
    filter_horizontal = ['class_types']
    inlines = [RankHistoryInline]
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'date_of_birth')
        }),
        ('Зэрэг цол', {
            'fields': ('kyu_rank', 'dan_rank', 'current_rank_date'),
            'description': 'Кюү эсвэл Дан зэргийн аль нэгийг сонгоно'
        }),
        ('Төлбөрийн мэдээлэл', {
            'fields': ('monthly_fee', 'fee_note'),
            'description': 'Сарын төлбөр болон тайлбар'
        }),
        ('Ангийн мэдээлэл', {
            'fields': ('class_types', 'enrollment_date', 'is_active')
        }),
        ('Хэрэглэгчийн холбоос', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    
    def get_rank(self, obj):
        return obj.get_rank_display_full()
    get_rank.short_description = 'Зэрэг'


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'get_rank', 'current_rank_date', 'hire_date', 'is_active']
    list_filter = ['is_active', 'hire_date', 'kyu_rank', 'dan_rank']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering = ['last_name', 'first_name']
    inlines = [RankHistoryInline]
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Зэрэг цол', {
            'fields': ('kyu_rank', 'dan_rank', 'current_rank_date'),
            'description': 'Кюү эсвэл Дан зэргийн аль нэгийг сонгоно'
        }),
        ('Ажлын мэдээлэл', {
            'fields': ('hire_date', 'is_active')
        }),
        ('Хэрэглэгчийн холбоос', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )
    
    def get_rank(self, obj):
        return obj.get_rank_display_full()
    get_rank.short_description = 'Зэрэг'


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ['class_type', 'date', 'weekday', 'start_time', 'end_time']
    list_filter = ['class_type', 'weekday', 'date']
    date_hierarchy = 'date'
    ordering = ['-date', 'start_time']


class InstructorAssignmentInline(admin.TabularInline):
    model = InstructorAssignment
    extra = 1


@admin.register(InstructorAssignment)
class InstructorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['instructor', 'session', 'role']
    list_filter = ['role', 'session__class_type', 'session__date']
    search_fields = ['instructor__first_name', 'instructor__last_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'is_present', 'recorded_by', 'recorded_at']
    list_filter = ['is_present', 'session__date', 'session__class_type']
    search_fields = ['student__first_name', 'student__last_name']
    date_hierarchy = 'session__date'
    ordering = ['-session__date']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'transaction_date', 'payment_month', 'is_verified']
    list_filter = ['is_verified', 'transaction_date', 'payment_month']
    search_fields = ['student__first_name', 'student__last_name', 'description', 'bank_reference']
    date_hierarchy = 'transaction_date'
    ordering = ['-transaction_date']
    
    fieldsets = (
        ('Банкны мэдээлэл', {
            'fields': ('transaction_date', 'amount', 'description', 'bank_reference')
        }),
        ('Холбох', {
            'fields': ('student', 'payment_month', 'is_verified')
        }),
    )


@admin.register(RankHistory)
class RankHistoryAdmin(admin.ModelAdmin):
    list_display = ['get_person', 'rank_type', 'rank_number', 'obtained_date']
    list_filter = ['rank_type', 'obtained_date']
    search_fields = ['student__first_name', 'student__last_name', 'instructor__first_name', 'instructor__last_name']
    date_hierarchy = 'obtained_date'
    ordering = ['-obtained_date']
    
    fieldsets = (
        ('Хэн', {
            'fields': ('student', 'instructor'),
            'description': 'Сурагч эсвэл багшийн аль нэгийг сонгоно'
        }),
        ('Зэрэг цолын мэдээлэл', {
            'fields': ('rank_type', 'rank_number', 'obtained_date', 'notes')
        }),
    )
    
    def get_person(self, obj):
        return obj.student or obj.instructor
    get_person.short_description = 'Хэн'


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1
    fields = ['student', 'payment_month', 'amount', 'notes']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_date', 'amount', 'payer_name', 'status', 'get_allocated_amount', 'get_remaining_amount', 'imported_at']
    list_filter = ['status', 'transaction_date', 'imported_at']
    search_fields = ['payer_name', 'description', 'reference_number']
    date_hierarchy = 'transaction_date'
    ordering = ['-transaction_date', '-imported_at']
    readonly_fields = ['imported_at', 'get_allocated_amount', 'get_remaining_amount']
    inlines = [PaymentAllocationInline]
    
    fieldsets = (
        ('Банкны гүйлгээний мэдээлэл', {
            'fields': ('transaction_date', 'amount', 'payer_name', 'description', 'reference_number')
        }),
        ('Төлөв', {
            'fields': ('status', 'notes', 'imported_at')
        }),
        ('Хуваарилалт', {
            'fields': ('get_allocated_amount', 'get_remaining_amount'),
            'description': 'Хуваарилагдсан болон үлдсэн дүн'
        }),
    )
    
    def get_allocated_amount(self, obj):
        return f"{obj.get_allocated_amount()}₮"
    get_allocated_amount.short_description = 'Хуваарилагдсан дүн'
    
    def get_remaining_amount(self, obj):
        return f"{obj.get_remaining_amount()}₮"
    get_remaining_amount.short_description = 'Үлдсэн дүн'


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ['bank_transaction', 'student', 'payment_month', 'amount', 'created_at']
    list_filter = ['payment_month', 'created_at']
    search_fields = ['student__first_name', 'student__last_name', 'bank_transaction__payer_name']
    date_hierarchy = 'payment_month'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Банкны гүйлгээ', {
            'fields': ('bank_transaction',)
        }),
        ('Хуваарилалт', {
            'fields': ('student', 'payment_month', 'amount', 'notes')
        }),
        ('Бусад', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(ExpenseAllocation)
class ExpenseAllocationAdmin(admin.ModelAdmin):
    list_display = ['bank_transaction', 'expense_category', 'expense_date', 'amount', 'created_at']
    list_filter = ['expense_category', 'expense_date', 'created_at']
    search_fields = ['expense_category__name', 'bank_transaction__description', 'notes']
    date_hierarchy = 'expense_date'
    ordering = ['-expense_date', '-created_at']
    
    fieldsets = (
        ('Банкны гүйлгээ', {
            'fields': ('bank_transaction',)
        }),
        ('Зардлын мэдээлэл', {
            'fields': ('expense_category', 'expense_date', 'amount', 'notes')
        }),
        ('Бусад', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
