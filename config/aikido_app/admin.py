from django.contrib import admin
from .models import Student, Instructor, ClassType, ClassSession, InstructorAssignment, Attendance, Payment, RankHistory


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
