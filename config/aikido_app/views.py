from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import calendar
from .models import Student, Instructor, ClassSession, Attendance, Payment, ClassType, InstructorAssignment


def login_view(request):
    """Нэвтрэх хуудас"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')  # Энэ нь имэйл байх болно
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Амжилттай нэвтэрлээ!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Имэйл эсвэл нууц үг буруу байна.')
    
    return render(request, 'aikido_app/login.html')


def logout_view(request):
    """Гарах"""
    auth_logout(request)
    messages.success(request, 'Амжилттай гарлаа!')
    return redirect('login')


def register_view(request):
    """Бүртгүүлэх хуудас"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Энэ нэвтрэх нэр аль хэдийн бүртгэгдсэн байна.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Энэ имэйл хаяг аль хэдийн бүртгэгдсэн байна.')
        elif password1 != password2:
            messages.error(request, 'Нууц үг таарахгүй байна.')
        elif len(password1) < 8:
            messages.error(request, 'Нууц үг хамгийн багадаа 8 тэмдэгт байх ёстой.')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Амжилттай бүртгэгдлээ! Нэвтрэж орно уу.')
            return redirect('login')
    
    return render(request, 'aikido_app/register.html')


@login_required
def dashboard(request):
    """Хяналтын самбар"""
    # Stats
    total_students = Student.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    
    # This week's classes
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    classes_this_week = ClassSession.objects.filter(
        date__gte=week_start,
        date__lte=week_end
    ).count()
    
    # This month's revenue
    month_start = today.replace(day=1)
    payments_this_month = Payment.objects.filter(
        transaction_date__gte=month_start,
        is_verified=True
    )
    total_revenue = payments_this_month.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # New students this month
    new_students_this_month = Student.objects.filter(
        enrollment_date__gte=month_start
    ).count()
    
    # Attendance last week
    last_week_start = week_start - timedelta(days=7)
    attendance_last_week = []
    for i in range(7):
        day = last_week_start + timedelta(days=i)
        day_sessions = ClassSession.objects.filter(date=day)
        total_attendance = Attendance.objects.filter(session__date=day).count()
        present_count = Attendance.objects.filter(session__date=day, is_present=True).count()
        
        percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        attendance_last_week.append({
            'date': day,
            'weekday': day.strftime('%a'),
            'total': total_attendance,
            'present': present_count,
            'percentage': percentage
        })
    
    # Upcoming sessions
    upcoming_sessions = ClassSession.objects.filter(
        date__gte=today
    ).order_by('date', 'start_time')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.select_related('student').order_by('-transaction_date')[:10]
    
    context = {
        'total_students': total_students,
        'total_instructors': total_instructors,
        'classes_this_week': classes_this_week,
        'total_revenue': total_revenue,
        'new_students_this_month': new_students_this_month,
        'payments_this_month': payments_this_month.count(),
        'attendance_last_week': attendance_last_week,
        'upcoming_sessions': upcoming_sessions,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'aikido_app/dashboard.html', context)


@login_required
def student_list(request):
    """Сурагчдын жагсаалт"""
    # Get sort parameter from query string
    sort_by = request.GET.get('sort', '-enrollment_date')
    
    # Valid sort options
    valid_sorts = {
        'name_asc': 'first_name',
        'name_desc': '-first_name',
        'date_asc': 'enrollment_date',
        'date_desc': '-enrollment_date',
        'rank_asc': 'dan_rank',
        'rank_desc': '-dan_rank',
    }
    
    # Use the sort parameter if valid, otherwise default
    order_by = valid_sorts.get(sort_by, 'first_name')
    
    students = Student.objects.all().order_by(order_by, 'last_name', 'first_name')
    
    return render(request, 'aikido_app/student_list.html', {
        'students': students,
        'current_sort': sort_by
    })


@login_required
def student_create(request):
    """Сурагч бүртгэх"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        date_of_birth = request.POST.get('date_of_birth') or None
        kyu_rank = request.POST.get('kyu_rank') or None
        dan_rank = request.POST.get('dan_rank') or None
        current_rank_date = request.POST.get('current_rank_date') or None
        monthly_fee = request.POST.get('monthly_fee') or None
        fee_note = request.POST.get('fee_note', '')
        class_types = request.POST.getlist('class_types')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not all([first_name, last_name, phone]):
            messages.error(request, 'Заавал бөглөх талбаруудыг бөглөнө үү.')
        else:
            try:
                student = Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    date_of_birth=date_of_birth,
                    kyu_rank=int(kyu_rank) if kyu_rank else None,
                    dan_rank=int(dan_rank) if dan_rank else None,
                    current_rank_date=current_rank_date,
                    monthly_fee=monthly_fee,
                    fee_note=fee_note,
                    is_active=is_active
                )
                if class_types:
                    student.class_types.set(class_types)
                messages.success(request, f'{student} амжилттай бүртгэгдлээ!')
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f'Алдаа гарлаа: {str(e)}')
    
    class_type_list = ClassType.objects.all()
    return render(request, 'aikido_app/student_form.html', {'class_types': class_type_list})


@login_required
def student_edit(request, pk):
    """Сурагчийн мэдээлэл засах"""
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        messages.error(request, 'Сурагч олдсонгүй.')
        return redirect('student_list')
    
    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.phone = request.POST.get('phone')
        student.email = request.POST.get('email', '')
        date_of_birth = request.POST.get('date_of_birth')
        student.date_of_birth = date_of_birth if date_of_birth else None
        kyu_rank = request.POST.get('kyu_rank')
        dan_rank = request.POST.get('dan_rank')
        current_rank_date = request.POST.get('current_rank_date')
        monthly_fee = request.POST.get('monthly_fee')
        student.kyu_rank = int(kyu_rank) if kyu_rank else None
        student.dan_rank = int(dan_rank) if dan_rank else None
        student.current_rank_date = current_rank_date if current_rank_date else None
        student.monthly_fee = monthly_fee if monthly_fee else None
        student.fee_note = request.POST.get('fee_note', '')
        student.is_active = request.POST.get('is_active') == 'on'
        class_types = request.POST.getlist('class_types')
        
        try:
            student.save()
            if class_types:
                student.class_types.set(class_types)
            messages.success(request, f'{student} амжилттай шинэчлэгдлээ!')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f'Алдаа гарлаа: {str(e)}')
    
    class_type_list = ClassType.objects.all()
    return render(request, 'aikido_app/student_form.html', {
        'student': student, 
        'class_types': class_type_list
    })


@login_required
def student_delete(request, pk):
    """Сурагч устгах"""
    try:
        student = Student.objects.get(pk=pk)
        name = str(student)
        student.delete()
        messages.success(request, f'{name} амжилттай устгагдлаа!')
    except Student.DoesNotExist:
        messages.error(request, 'Сурагч олдсонгүй.')
    return redirect('student_list')


@login_required
def instructor_list(request):
    """Багш нарын жагсаалт"""
    # Get sort parameter from query string
    sort_by = request.GET.get('sort', 'name_asc')
    
    # Valid sort options
    valid_sorts = {
        'name_asc': 'last_name',
        'name_desc': '-last_name',
        'date_asc': 'hire_date',
        'date_desc': '-hire_date',
        'rank_asc': 'dan_rank',
        'rank_desc': '-dan_rank',
    }
    
    # Use the sort parameter if valid, otherwise default
    order_by = valid_sorts.get(sort_by, 'last_name')
    
    # Get filter parameter
    show_inactive = request.GET.get('show_inactive', 'false') == 'true'
    
    if show_inactive:
        instructors = Instructor.objects.all()
    else:
        instructors = Instructor.objects.filter(is_active=True)
    
    instructors = instructors.order_by(order_by, 'last_name', 'first_name')
    
    # Calculate statistics for each instructor
    for instructor in instructors:
        # Count lead and assistant roles by class type
        lead_morning = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='LEAD',
            session__class_type__name=ClassType.MORNING
        ).count()
        
        assistant_morning = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='ASSISTANT',
            session__class_type__name=ClassType.MORNING
        ).count()
        
        lead_evening = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='LEAD',
            session__class_type__name=ClassType.EVENING
        ).count()
        
        assistant_evening = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='ASSISTANT',
            session__class_type__name=ClassType.EVENING
        ).count()
        
        lead_children = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='LEAD',
            session__class_type__name=ClassType.CHILDREN
        ).count()
        
        assistant_children = InstructorAssignment.objects.filter(
            instructor=instructor,
            role='ASSISTANT',
            session__class_type__name=ClassType.CHILDREN
        ).count()
        
        instructor.stats = {
            'morning': {'lead': lead_morning, 'assistant': assistant_morning},
            'evening': {'lead': lead_evening, 'assistant': assistant_evening},
            'children': {'lead': lead_children, 'assistant': assistant_children},
            'total_lead': lead_morning + lead_evening + lead_children,
            'total_assistant': assistant_morning + assistant_evening + assistant_children,
        }
    
    return render(request, 'aikido_app/instructor_list.html', {
        'instructors': instructors,
        'current_sort': sort_by,
        'show_inactive': show_inactive
    })


@login_required
def instructor_create(request):
    """Багш бүртгэх"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        hire_date = request.POST.get('hire_date')
        kyu_rank = request.POST.get('kyu_rank') or None
        dan_rank = request.POST.get('dan_rank') or None
        current_rank_date = request.POST.get('current_rank_date') or None
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not all([first_name, last_name, phone, hire_date]):
            messages.error(request, 'Заавал бөглөх талбаруудыг бөглөнө үү.')
        else:
            try:
                instructor = Instructor.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    hire_date=hire_date,
                    kyu_rank=int(kyu_rank) if kyu_rank else None,
                    dan_rank=int(dan_rank) if dan_rank else None,
                    current_rank_date=current_rank_date if current_rank_date else None,
                    is_active=is_active
                )
                messages.success(request, f'{instructor} амжилттай бүртгэгдлээ!')
                return redirect('instructor_list')
            except Exception as e:
                messages.error(request, f'Алдаа гарлаа: {str(e)}')
    
    return render(request, 'aikido_app/instructor_form.html')


@login_required
def instructor_edit(request, pk):
    """Багшийн мэдээлэл засах"""
    try:
        instructor = Instructor.objects.get(pk=pk)
    except Instructor.DoesNotExist:
        messages.error(request, 'Багш олдсонгүй.')
        return redirect('instructor_list')
    
    if request.method == 'POST':
        instructor.first_name = request.POST.get('first_name')
        instructor.last_name = request.POST.get('last_name')
        instructor.phone = request.POST.get('phone')
        instructor.email = request.POST.get('email', '')
        instructor.hire_date = request.POST.get('hire_date')
        kyu_rank = request.POST.get('kyu_rank')
        dan_rank = request.POST.get('dan_rank')
        current_rank_date = request.POST.get('current_rank_date')
        instructor.kyu_rank = int(kyu_rank) if kyu_rank else None
        instructor.dan_rank = int(dan_rank) if dan_rank else None
        instructor.current_rank_date = current_rank_date if current_rank_date else None
        instructor.is_active = request.POST.get('is_active') == 'on'
        
        try:
            instructor.save()
            messages.success(request, f'{instructor} амжилттай шинэчлэгдлээ!')
            return redirect('instructor_list')
        except Exception as e:
            messages.error(request, f'Алдаа гарлаа: {str(e)}')
    
    return render(request, 'aikido_app/instructor_form.html', {'instructor': instructor})


@login_required
def instructor_delete(request, pk):
    """Багш устгах"""
    try:
        instructor = Instructor.objects.get(pk=pk)
        name = str(instructor)
        instructor.delete()
        messages.success(request, f'{name} амжилттай устгагдлаа!')
    except Instructor.DoesNotExist:
        messages.error(request, 'Багш олдсонгүй.')
    except Exception as e:
        messages.error(request, f'Алдаа гарлаа: {str(e)}')
    
    return redirect('instructor_list')


@login_required
def class_schedule(request):
    """Хичээлийн хуваарь"""
    weekdays = ['Даваа', 'Мягмар', 'Лхагва', 'Пүрэв', 'Баасан', 'Бямба', 'Ням']
    return render(request, 'aikido_app/class_schedule.html', {'weekdays': weekdays})


@login_required
def attendance_list(request):
    """Ирцийн жагсаалт"""
    attendances = Attendance.objects.select_related(
        'student', 'session', 'recorded_by'
    ).order_by('-session__date')[:50]
    return render(request, 'aikido_app/attendance_list.html', {'attendances': attendances})


@login_required
def payment_list(request):
    """Төлбөрийн жагсаалт"""
    payments = Payment.objects.select_related('student').order_by('-transaction_date')[:50]
    return render(request, 'aikido_app/payment_list.html', {'payments': payments})


@login_required
def attendance_record(request):
    """Ирц бүртгэх - Багшийн хуудас"""
    # Get current user's instructor record if exists
    try:
        instructor = Instructor.objects.get(user=request.user)
    except Instructor.DoesNotExist:
        # Check by email
        try:
            instructor = Instructor.objects.get(email=request.user.email)
        except Instructor.DoesNotExist:
            instructor = None
    
    # Handle AJAX POST request for saving attendance
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            attendance_data = data.get('attendance', [])
            instructor_assignments = data.get('instructor_assignments', [])
            class_type_name = data.get('class_type', '')
            
            # Save instructor assignments first
            for assignment_data in instructor_assignments:
                date_str = assignment_data.get('date')
                lead_instructor_id = assignment_data.get('lead_instructor_id')
                assistant_instructor_id = assignment_data.get('assistant_instructor_id')
                
                # Handle "NO_CLASS" marker - save empty session to indicate class was cancelled
                if lead_instructor_id == 'NO_CLASS' or assistant_instructor_id == 'NO_CLASS':
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # Get or create class session
                        class_type = ClassType.objects.filter(name=class_type_name).first() or ClassType.objects.first()
                        session, created = ClassSession.objects.get_or_create(
                            date=date_obj,
                            class_type=class_type,
                            defaults={
                                'weekday': date_obj.weekday(),
                                'start_time': '09:00',
                                'end_time': '11:00',
                            }
                        )
                        
                        # Clear all existing assignments - this marks it as "no class"
                        InstructorAssignment.objects.filter(session=session).delete()
                    except Exception as e:
                        print(f"Error saving NO_CLASS marker: {e}")
                    continue
                
                # Skip if both are empty (and not NO_CLASS)
                if not lead_instructor_id and not assistant_instructor_id:
                    continue
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    # Get or create class session
                    class_type = ClassType.objects.filter(name=class_type_name).first() or ClassType.objects.first()
                    session, created = ClassSession.objects.get_or_create(
                        date=date_obj,
                        class_type=class_type,
                        defaults={
                            'weekday': date_obj.weekday(),
                            'start_time': '09:00',
                            'end_time': '11:00',
                        }
                    )
                    
                    # Clear existing assignments for this session
                    InstructorAssignment.objects.filter(session=session).delete()
                    
                    # Create new assignments only if instructor is selected
                    if lead_instructor_id and lead_instructor_id.strip():
                        try:
                            lead_instructor = Instructor.objects.get(id=int(lead_instructor_id))
                            InstructorAssignment.objects.create(
                                session=session,
                                instructor=lead_instructor,
                                role='LEAD'
                            )
                        except (Instructor.DoesNotExist, ValueError):
                            pass
                    
                    if assistant_instructor_id and assistant_instructor_id.strip():
                        try:
                            assistant_instructor = Instructor.objects.get(id=int(assistant_instructor_id))
                            InstructorAssignment.objects.create(
                                session=session,
                                instructor=assistant_instructor,
                                role='ASSISTANT'
                            )
                        except (Instructor.DoesNotExist, ValueError):
                            pass
                except Exception as e:
                    print(f"Error saving instructor assignment: {e}")
            
            # Save attendance
            for item in attendance_data:
                student_id = item.get('student_id')
                date_str = item.get('date')
                
                try:
                    student = Student.objects.get(id=student_id)
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    # Get class type from request data
                    class_type = ClassType.objects.filter(name=class_type_name).first()
                    if not class_type:
                        class_type = student.class_types.first() or ClassType.objects.first()
                    
                    # Find or create session for this date and class type
                    session, created = ClassSession.objects.get_or_create(
                        date=date_obj,
                        class_type=class_type,
                        defaults={
                            'weekday': date_obj.weekday(),
                            'start_time': '09:00',
                            'end_time': '11:00',
                        }
                    )
                    
                    # Create or update attendance
                    Attendance.objects.update_or_create(
                        session=session,
                        student=student,
                        defaults={
                            'is_present': True,
                            'recorded_by': instructor
                        }
                    )
                except Student.DoesNotExist:
                    pass
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - display attendance form
    selected_class_type = request.GET.get('class_type', '')
    selected_month = request.GET.get('month', datetime.now().strftime('%Y-%m'))
    
    # Parse selected month
    year, month = map(int, selected_month.split('-'))
    
    # Get all class types
    class_types = ClassType.objects.all()
    
    # Filter students by class type
    students = Student.objects.filter(is_active=True).prefetch_related('class_types')
    
    if selected_class_type:
        students = students.filter(class_types__name=selected_class_type)
    
    students = students.order_by('first_name', 'last_name')
    
    # Generate dates based on class type
    dates = []
    
    if selected_class_type:
        # Get the ClassType object
        try:
            class_type_obj = ClassType.objects.get(name=selected_class_type)
            
            # Determine which weekdays to show
            if class_type_obj.name in [ClassType.MORNING, ClassType.EVENING]:
                # Mon, Wed, Fri (0, 2, 4)
                target_weekdays = [0, 2, 4]
                weekday_names = ['Даваа', 'Лхагва', 'Баасан']
            else:  # Children
                # Sat, Sun (5, 6)
                target_weekdays = [5, 6]
                weekday_names = ['Бямба', 'Ням']
        except ClassType.DoesNotExist:
            target_weekdays = [0, 2, 4, 5, 6]
            weekday_names = ['Даваа', 'Лхагва', 'Баасан', 'Бямба', 'Ням']
    else:
        # Show all days: Mon, Wed, Fri, Sat, Sun
        target_weekdays = [0, 2, 4, 5, 6]
        weekday_names = ['Даваа', 'Лхагва', 'Баасан', 'Бямба', 'Ням']
    
    # Get all days in the month
    num_days = calendar.monthrange(year, month)[1]
    
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        if date.weekday() in target_weekdays:
            weekday_index = target_weekdays.index(date.weekday())
            dates.append({
                'date': date,
                'weekday': weekday_names[weekday_index]
            })
    
    # Get existing attendance for these students and dates
    if students.exists() and dates:
        date_list = [d['date'] for d in dates]
        attendances = Attendance.objects.filter(
            student__in=students,
            session__date__in=date_list,
            is_present=True
        ).select_related('student', 'session')
        
        # Build attendance map
        attendance_map = {}
        for att in attendances:
            if att.student.id not in attendance_map:
                attendance_map[att.student.id] = set()
            attendance_map[att.student.id].add(att.session.date.strftime('%Y-%m-%d'))
        
        # Add attendance info to students
        for student in students:
            student.attendance_dates = attendance_map.get(student.id, set())
            student.attendance_count = len(student.attendance_dates)
    
    # Get all active instructors for assignment
    all_instructors = Instructor.objects.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Determine default instructors based on class type
    # Using actual instructor names from database:
    # ID 3: Галбадрах (Хүүхэд)
    # ID 1: Амгаланбаяр (Өглөө)
    # ID 2: Баясгалан (Орой)
    default_lead = None
    default_assistant = None
    
    try:
        if selected_class_type == ClassType.CHILDREN:
            # Хүүхдийн анги - Галбадрах
            default_instructor = Instructor.objects.get(id=3)  # Галбадрах
            default_lead = default_instructor
            default_assistant = default_instructor
        elif selected_class_type == ClassType.MORNING:
            # Өглөөний анги - Амгаланбаяр
            default_instructor = Instructor.objects.get(id=1)  # Амгаланбаяр
            default_lead = default_instructor
            default_assistant = default_instructor
        elif selected_class_type == ClassType.EVENING:
            # Оройны анги - Баясгалан
            default_instructor = Instructor.objects.get(id=2)  # Баясгалан
            default_lead = default_instructor
            default_assistant = default_instructor
    except Instructor.DoesNotExist:
        pass
    
    # Get existing instructor assignments for the dates
    if dates:
        date_list = [d['date'] for d in dates]
        
        # Filter sessions by date and optionally by class_type
        sessions_query = ClassSession.objects.filter(date__in=date_list)
        if selected_class_type:
            sessions_query = sessions_query.filter(class_type__name=selected_class_type)
        
        sessions_with_instructors = sessions_query.prefetch_related('instructor_assignments__instructor')
        
        # Build instructor assignment map: {date: {'lead': instructor, 'assistant': instructor, 'class_type': name, 'has_assignments': bool}}
        instructor_assignment_map = {}
        for session in sessions_with_instructors:
            date_str = session.date.strftime('%Y-%m-%d')
            has_assignments = session.instructor_assignments.exists()
            
            instructor_assignment_map[date_str] = {
                'class_type': session.class_type.name,
                'has_assignments': has_assignments
            }
            
            for assignment in session.instructor_assignments.all():
                if assignment.role == 'LEAD':
                    instructor_assignment_map[date_str]['lead'] = assignment.instructor
                elif assignment.role == 'ASSISTANT':
                    instructor_assignment_map[date_str]['assistant'] = assignment.instructor
        
        # Add instructor info to dates
        for date_item in dates:
            date_str = date_item['date'].strftime('%Y-%m-%d')
            assignments = instructor_assignment_map.get(date_str, {})
            session_class_type = assignments.get('class_type')
            has_assignments = assignments.get('has_assignments', False)
            
            # Decision logic for showing instructors:
            if selected_class_type:
                # A specific class type is selected
                if not session_class_type:
                    # No session exists - show defaults
                    date_item['lead_instructor'] = default_lead
                    date_item['assistant_instructor'] = default_assistant
                elif session_class_type == selected_class_type:
                    # Session exists and matches selected class type
                    if has_assignments:
                        # Has instructor assignments - show them
                        date_item['lead_instructor'] = assignments.get('lead')
                        date_item['assistant_instructor'] = assignments.get('assistant')
                    else:
                        # Session exists but no instructors assigned yet - show defaults
                        date_item['lead_instructor'] = default_lead
                        date_item['assistant_instructor'] = default_assistant
                else:
                    # Session exists but different class type - show nothing (empty)
                    date_item['lead_instructor'] = None
                    date_item['assistant_instructor'] = None
            else:
                # No class type selected (viewing all classes)
                # Only show assigned instructors, no defaults
                date_item['lead_instructor'] = assignments.get('lead')
                date_item['assistant_instructor'] = assignments.get('assistant')
    
    # Calculate instructor statistics for the selected month and class type
    instructor_stats = []
    if dates:  # Changed: removed selected_class_type requirement
        date_list = [d['date'] for d in dates]
        
        for instructor in all_instructors:
            # Calculate stats by class type
            stats_by_class = {}
            total_lead = 0
            total_assistant = 0
            
            # Get stats for each class type
            for class_type in class_types:
                lead_count = InstructorAssignment.objects.filter(
                    instructor=instructor,
                    role='LEAD',
                    session__date__in=date_list,
                    session__class_type__name=class_type.name
                ).count()
                
                assistant_count = InstructorAssignment.objects.filter(
                    instructor=instructor,
                    role='ASSISTANT',
                    session__date__in=date_list,
                    session__class_type__name=class_type.name
                ).count()
                
                if lead_count > 0 or assistant_count > 0:
                    stats_by_class[class_type.name] = {
                        'class_type': class_type,
                        'lead': lead_count,
                        'assistant': assistant_count,
                        'total': lead_count + assistant_count
                    }
                
                total_lead += lead_count
                total_assistant += assistant_count
            
            total = total_lead + total_assistant
            
            # Always show instructors if they have any stats (regardless of selected_class_type)
            if total > 0:
                # If a specific class type is selected, use that class stats for main counts
                if selected_class_type and selected_class_type in stats_by_class:
                    instructor_stats.append({
                        'instructor': instructor,
                        'stats_by_class': stats_by_class,
                        'lead_count': stats_by_class[selected_class_type]['lead'],
                        'assistant_count': stats_by_class[selected_class_type]['assistant'],
                        'total': stats_by_class[selected_class_type]['total']
                    })
                else:
                    # No specific class selected or instructor doesn't have stats for selected class
                    # Show total across all classes
                    instructor_stats.append({
                        'instructor': instructor,
                        'stats_by_class': stats_by_class,
                        'lead_count': total_lead,
                        'assistant_count': total_assistant,
                        'total': total
                    })
        
        # Sort by total descending
        instructor_stats.sort(key=lambda x: x['total'], reverse=True)
    
    context = {
        'class_types': class_types,
        'selected_class_type': selected_class_type,
        'selected_month': selected_month,
        'students': students,
        'dates': dates,
        'all_instructors': all_instructors,
        'default_lead': default_lead,
        'default_assistant': default_assistant,
        'instructor_stats': instructor_stats,
    }
    
    return render(request, 'aikido_app/attendance_record.html', context)


@csrf_exempt
@login_required
def assign_instructors(request):
    """Тухайн өдрийн ахлах болон туслах багшийг томилох"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            lead_instructor_id = data.get('lead_instructor_id')
            assistant_instructor_id = data.get('assistant_instructor_id')
            class_type_name = data.get('class_type')
            
            # Validation
            if not date_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Огноо дутуу байна'
                }, status=400)
            
            # Parse date
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Огнооны формат буруу: {str(e)}'
                }, status=400)
            
            # Get or create class session for this date
            class_type = ClassType.objects.filter(name=class_type_name).first() or ClassType.objects.first()
            
            if not class_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Ангийн төрөл олдсонгүй'
                }, status=400)
            
            session, created = ClassSession.objects.get_or_create(
                date=date_obj,
                class_type=class_type,
                defaults={
                    'weekday': date_obj.weekday(),
                    'start_time': '09:00',
                    'end_time': '11:00',
                }
            )
            
            # Clear existing instructor assignments for this session
            InstructorAssignment.objects.filter(session=session).delete()
            
            # Handle NO_CLASS case - if either instructor is NO_CLASS, don't assign anyone
            if lead_instructor_id == 'NO_CLASS' or assistant_instructor_id == 'NO_CLASS':
                return JsonResponse({
                    'success': True,
                    'message': 'Хичээл ороогүй гэж тэмдэглэгдлээ'
                })
            
            # Assign lead instructor
            if lead_instructor_id:
                try:
                    lead_instructor = Instructor.objects.get(id=lead_instructor_id)
                    InstructorAssignment.objects.create(
                        session=session,
                        instructor=lead_instructor,
                        role='LEAD'
                    )
                except Instructor.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Ахлах багш (ID: {lead_instructor_id}) олдсонгүй'
                    }, status=400)
            
            # Assign assistant instructor
            if assistant_instructor_id:
                try:
                    assistant_instructor = Instructor.objects.get(id=assistant_instructor_id)
                    InstructorAssignment.objects.create(
                        session=session,
                        instructor=assistant_instructor,
                        role='ASSISTANT'
                    )
                except Instructor.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Туслах багш (ID: {assistant_instructor_id}) олдсонгүй'
                    }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': 'Багш амжилттай томилогдлоо'
            })
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'JSON алдаа: {str(e)}'
            }, status=400)
        except Exception as e:
            # Log the full error for debugging
            import traceback
            print(f"Error in assign_instructors: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f'Алдаа гарлаа: {str(e)}'
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
