from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class RegisterUserTestCase(TestCase):
    def setUp(self):
        """Инициализация перед выполнением каждого теста"""

        self.data = {
            'username': 'user1',
            'email': 'user@user.ru',
            'password1': '12345678Aa-',
            'password2': '12345678Aa-',
        }

        self.user_model = get_user_model()


    def test_form_registration_get(self):
        """Тест на получение формы регистрации"""

        path = reverse('users:register')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/register.html')

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_user_registration_success(self):
        """Тест на успешную регистрацию пользователя"""

        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(self.user_model.objects.filter(username=self.data['username']).exists())

    def test_user_registration_password_error(self):
        """Тест на ошибку при регистрации пользователя с несовпадающими паролями"""

        self.data['password2'] = '12345678A'
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Введенные пароли не совпадают.")

    def test_user_registration_user_exists_error(self):
        """Тест на ошибку при регистрации пользователя с существующим именем"""

        self.user_model.objects.create(username=self.data['username'])
        path = reverse('users:register')
        response = self.client.post(path, self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пользователь с таким именем уже существует.")



