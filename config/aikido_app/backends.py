from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Имэйл хаяг ашиглан нэвтрэх боломжтой болгох authentication backend
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Имэйл хаягаар хайх
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Username-ээр ч оролдох
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        return None
