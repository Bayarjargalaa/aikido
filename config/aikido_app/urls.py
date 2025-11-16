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
]
