from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import (LoginUserForm, ProfileUserForm, RegisterUserForm,
                    UserPasswordChangeForm)
from .models import EmailVerification


class LoginUser(LoginView):
    """Класс представления страницы авторизации"""

    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class RegisterUser(CreateView):
    """Класс представления страницы регистрации"""

    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': "Регистрация"}
    success_url = reverse_lazy('users:login')


class Profile(LoginRequiredMixin, UpdateView):
    """Класс представления страницы профиля пользователя"""

    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя", 'default_img': settings.DEFAULT_USER_IMAGE}

    def get_success_url(self) -> str:
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None) -> get_user_model():
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    """Класс представления для изменения пароля пользователя"""

    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
    extra_context = {'title': "Изменение пароля"}


class EmailVerificationView(TemplateView):
    """Класс представления для подтверждения электронной почты"""

    title = 'Подтверждение электронной почты'
    template_name = 'users/email_verification_done.html'

    def get(self, request, *args, **kwargs) -> HttpResponseRedirect:
        code = kwargs['code']
        user = get_user_model().objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return redirect('users:login')
