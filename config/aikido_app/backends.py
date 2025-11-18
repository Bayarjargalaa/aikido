from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Имэйл хаяг ашиглан нэвтрэх боломжтой болгох authentication backend
    Багш болон сурагчийн имэйлээр автоматаар профайл холбох
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Имэйл хаягаар хайх
            user = User.objects.get(email=username)
            if user.check_password(password):
                # After successful authentication, link profiles
                self._link_profiles(user)
                return user
        except User.DoesNotExist:
            # Username-ээр ч оролдох
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    # After successful authentication, link profiles
                    self._link_profiles(user)
                    return user
            except User.DoesNotExist:
                return None
        return None
    
    def _link_profiles(self, user):
        """
        Хэрэглэгчийн имэйлээр багш эсвэл сурагчтай холбох
        """
        from config.aikido_app.models import Instructor, Student
        
        if not user.email:
            return
        
        # Check if already linked
        has_instructor = hasattr(user, 'instructor_profile')
        has_student = hasattr(user, 'student_profile')
        
        if has_instructor or has_student:
            return  # Already linked
        
        # Try to find instructor by email
        try:
            instructor = Instructor.objects.get(email=user.email, user__isnull=True)
            instructor.user = user
            instructor.save()
            return
        except Instructor.DoesNotExist:
            pass
        except Instructor.MultipleObjectsReturned:
            # Multiple instructors with same email, link to first one without user
            instructor = Instructor.objects.filter(email=user.email, user__isnull=True).first()
            if instructor:
                instructor.user = user
                instructor.save()
                return
        
        # Try to find student by email
        try:
            student = Student.objects.get(email=user.email, user__isnull=True)
            student.user = user
            student.save()
        except Student.DoesNotExist:
            pass
        except Student.MultipleObjectsReturned:
            # Multiple students with same email, link to first one without user
            student = Student.objects.filter(email=user.email, user__isnull=True).first()
            if student:
                student.user = user
                student.save()

