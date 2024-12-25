from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            # Check if the user with the given email exists
            user = get_user_model().objects.get(email=email)
            # If the user exists, check if the password matches
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
