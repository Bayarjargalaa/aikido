from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Public Pages (Даалгаврын шаардлага)
    path('', views.LandingPageView.as_view(), name='landing'),
    path('about/', views.AboutPageView.as_view(), name='about'),
    
    # Dashboard (Admin only)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Students - Class-Based Views (Даалгаврын шаардлага)
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Instructors - Class-Based Views (Даалгаврын шаардлага)
    path('instructors/', views.InstructorListView.as_view(), name='instructor_list'),
    path('instructors/create/', views.instructor_create, name='instructor_create'),
    path('instructors/<int:pk>/edit/', views.instructor_edit, name='instructor_edit'),
    path('instructors/<int:pk>/delete/', views.instructor_delete, name='instructor_delete'),
    
    # Class Schedule & Attendance
    path('schedule/', views.class_schedule, name='class_schedule'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/record/', views.attendance_record, name='attendance_record'),
    path('attendance/assign-instructors/', views.assign_instructors, name='assign_instructors'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('seminar-payments/', views.seminar_payment_list, name='seminar_payment_list'),
    path('membership-payments/', views.membership_payment_list, name='membership_payment_list'),
    path('income/', views.income_list, name='income_list'),
    
    # Monthly payment reports
    path('monthly-payment-report/', views.monthly_payment_report, name='monthly_payment_report'),
    path('instructor-payments/', views.instructor_payment_list, name='instructor_payment_list'),
    path('instructor-payments/<int:payment_id>/mark-paid/', views.mark_instructor_payment_paid, name='mark_instructor_payment_paid'),
    path('instructor-payments/calculate-from-attendance/', views.calculate_instructor_payments_from_attendance, name='calculate_instructor_payments_from_attendance'),
    path('federation-payments/', views.federation_payment_list, name='federation_payment_list'),
    path('federation-payments/<int:payment_id>/mark-paid/', views.mark_federation_payment_paid, name='mark_federation_payment_paid'),
    
    # Bank transactions
    path('bank-transactions/', views.bank_transaction_list, name='bank_transaction_list'),
    path('bank-transactions/upload/', views.bank_transaction_upload, name='bank_transaction_upload'),
    path('bank-transactions/<int:transaction_id>/match/', views.bank_transaction_match, name='bank_transaction_match'),
    path('payment-allocation/<int:allocation_id>/delete/', views.delete_payment_allocation, name='delete_payment_allocation'),
    path('seminar-payment-allocation/<int:allocation_id>/delete/', views.delete_seminar_payment_allocation, name='delete_seminar_payment_allocation'),
    path('membership-payment-allocation/<int:allocation_id>/delete/', views.delete_membership_payment_allocation, name='delete_membership_payment_allocation'),
    path('expense-allocation/<int:allocation_id>/delete/', views.delete_expense_allocation, name='delete_expense_allocation'),
    path('instructor-payment-allocation/<int:allocation_id>/delete/', views.delete_instructor_payment_allocation, name='delete_instructor_payment_allocation'),
    path('income-allocation/<int:allocation_id>/delete/', views.delete_income_allocation, name='delete_income_allocation'),
]
