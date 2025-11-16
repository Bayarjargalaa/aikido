from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('instructors/create/', views.instructor_create, name='instructor_create'),
    path('instructors/<int:pk>/edit/', views.instructor_edit, name='instructor_edit'),
    path('instructors/<int:pk>/delete/', views.instructor_delete, name='instructor_delete'),
    path('schedule/', views.class_schedule, name='class_schedule'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/record/', views.attendance_record, name='attendance_record'),
    path('attendance/assign-instructors/', views.assign_instructors, name='assign_instructors'),
    path('payments/', views.payment_list, name='payment_list'),
    path('seminar-payments/', views.seminar_payment_list, name='seminar_payment_list'),
    path('membership-payments/', views.membership_payment_list, name='membership_payment_list'),
    path('income/', views.income_list, name='income_list'),
    
    # Bank transactions
    path('bank-transactions/', views.bank_transaction_list, name='bank_transaction_list'),
    path('bank-transactions/upload/', views.bank_transaction_upload, name='bank_transaction_upload'),
    path('bank-transactions/<int:transaction_id>/match/', views.bank_transaction_match, name='bank_transaction_match'),
    path('payment-allocation/<int:allocation_id>/delete/', views.delete_payment_allocation, name='delete_payment_allocation'),
    path('expense-allocation/<int:allocation_id>/delete/', views.delete_expense_allocation, name='delete_expense_allocation'),
    path('income-allocation/<int:allocation_id>/delete/', views.delete_income_allocation, name='delete_income_allocation'),
]
