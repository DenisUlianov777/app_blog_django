import uuid
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from users.models import EmailVerification


@shared_task
def send_email_verification(user_id: int) -> None:
    """Отправляет письмо для верификации электронной почты пользователя на email"""
    user = get_user_model().objects.get(id=user_id)
    expiration = now() + timedelta(hours=48)
    record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
    record.send_verification_email()
