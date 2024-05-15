from http import HTTPStatus

from django.test import TestCase

from .models import *


class PageTestCase(TestCase):
    fixtures = ['bike.json', 'category.json', 'tags.json', 'userPostRelation.json', 'user.json']

    def setUp(self):
        """Инициализация перед выполнением каждого теста"""

    def test_homepage(self):
        """Тест главной страницы"""

        path = reverse('home')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'bike_app/index.html')
        self.assertEqual(response.context_data['title'], 'Главная страница')

    def test_redirect_addpage(self):
        """Тест редиректа при попытке добавить пост неавторизованным пользователем"""

        path = reverse('add_page')
        redirect_uri = reverse('users:login') + '?next=' + path
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)

    def test_data_mainpage(self):
        """Тест данных главной страницы"""

        b = Bike.published.all().select_related('cat')
        path = reverse('home')
        response = self.client.get(path)
        self.assertQuerysetEqual(response.context_data['posts'], b[:1])

    def test_paginate_mainpage(self):
        """Тест пагинации"""

        path = reverse('home')
        page = 2
        paginate_by = 1
        response = self.client.get(path + f'?page={page}')
        b = Bike.published.all().select_related('cat')
        self.assertQuerysetEqual(response.context_data['posts'], b[(page - 1) * paginate_by:page * paginate_by])

    def test_content_post(self):
        """Тест содержания поста"""

        b = Bike.published.get(pk=1)
        path = reverse('post', args=[b.slug])
        response = self.client.get(path)
        self.assertEqual(b.content, response.context_data['post'].content)

    def tearDown(self):
        "Действия после выполнения каждого теста"
