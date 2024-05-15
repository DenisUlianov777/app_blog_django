from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from users.utils import CustomStorage


class User(AbstractUser):
    """Расширенная модель User"""

    photo = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name="Фотография", storage=CustomStorage())
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    is_verified_email = models.BooleanField(default=False)


class EmailVerification(models.Model):
    """Модель верификации пользователя чераз email"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    code = models.UUIDField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'EmailVerification object for {self.user.email}'

    def send_verification_email(self) -> None:
        """Формирование письма для подтверждения учетной записи"""

        link = reverse('users:email_verification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = self.request.build_absolute_uri(link)
        subject = f'Подтверждение учетной записи для {self.user.username}'
        message = f'Для подтверждения учетной записи для {self.user.email} перейдите по ссылке: {verification_link}'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self) -> bool:
        """Проверка на актуальность кода для верификации(срок службы 48 часов)"""

        return True if now() >= self.expiration else False
