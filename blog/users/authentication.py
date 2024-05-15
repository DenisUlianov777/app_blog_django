from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class EmailAuthBackend(BaseBackend):
    """Авторизация по email адресу"""

    users_model = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs) -> Optional[get_user_model()]:
        try:
            user = self.users_model.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (self.users_model.DoesNotExist, self.users_model.MultipleObjectsReturned):
            return None

    def get_user(self, user_id) -> Optional[get_user_model()]:
        try:
            return self.users_model.objects.get(pk=user_id)
        except self.users_model.DoesNotExist:
            return None
