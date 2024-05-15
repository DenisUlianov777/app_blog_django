import json
from http import HTTPStatus

from django.db.models import Avg, Case, Count, Q, When
from django.test import TestCase
from rest_framework.test import APITestCase

from api.v1.serializers import BikesSerializer
from bike_app.models import *


class MyApiTestCase(APITestCase):
    """Тест-кейс для тестирования API"""

    def setUp(self):
        """Данные для тестирования"""

        self.user = get_user_model().objects.create(username='test_username')
        self.c_1 = Category.objects.create(name='cat1')
        self.b_1 = Bike.published.create(title='post1', content='cont1', cat_id=self.c_1.id, auth_user=self.user)
        self.b_2 = Bike.published.create(title='post2', content='cont2', cat_id=self.c_1.id)

        UserPostRelation.objects.create(auth_user=self.user, bike=self.b_1, like=True,
                                        rate=5)

    def test_get_object(self):
        """Тест получения объекта"""
        post = Bike.objects.filter(id=self.b_1.id).annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')
        path = reverse('bike-detail', args=(self.b_1.id,))
        self.client.force_authenticate(user=self.user)
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        serializer_data = BikesSerializer(post[0]).data
        self.assertEqual(serializer_data, response.data)

    def test_get_list(self):
        """Тест получения списка объектов"""

        path = reverse('bike-list')
        response = self.client.get(path)
        posts = Bike.objects.all().annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')
        serializer_data = BikesSerializer(posts, many=True).data
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(serializer_data, response.data['results'])
        self.assertEqual(serializer_data[1]['rating'], '5.00')
        self.assertEqual(serializer_data[1]['count_likes'], 1)

    def test_create(self):
        """Тест создания объекта"""

        count_b = Bike.objects.all().count()
        path = reverse('bike-list')
        data = {
            "title": 'post3',
            "content": 'cont3',
            "cat": self.c_1.id
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(path, data=json_data,
                                    content_type='application/json')
        self.assertEqual(HTTPStatus.CREATED, response.status_code)
        self.assertEqual(count_b + 1, Bike.objects.all().count())

    def test_update(self):
        """Тест изменения объекта"""

        path = reverse('bike-detail', args=(self.b_1.id,))
        data = {
            "title": 'post3',
            "content": 'cont3',
            "cat": self.c_1.id
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(path, data=json_data,
                                   content_type='application/json')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.b_1.refresh_from_db()
        self.assertEqual('cont3', self.b_1.content)

    def test_delete(self):
        """Тест удаления объекта"""

        count_b = Bike.objects.all().count()
        path = reverse('bike-detail', args=(self.b_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(path)
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertEqual(count_b - 1, Bike.objects.all().count())

    #
    def test_not_owner(self):
        """Тест на редактирование не автором поста"""

        self.user2 = get_user_model().objects.create(username='test_username2')

        path = reverse('bike-detail', args=(self.b_1.id,))
        data = {
            "title": 'post3',
            "content": 'cont3',
            "cat": self.c_1.id
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(path, data=json_data,
                                   content_type='application/json')
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.b_1.refresh_from_db()
        self.assertEqual('cont1', self.b_1.content)

    def test_get_filter(self):
        """Тест фильтра"""

        url = reverse('bike-list')
        books = Bike.objects.filter(id=self.b_1.id).annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')
        response = self.client.get(url, data={'title': 'post1'})
        serializer_data = BikesSerializer(books, many=True).data
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])

    def test_get_search(self):
        """Тест поиска"""

        url = reverse('bike-list')
        post = Bike.objects.filter(id=self.b_2.id).annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')
        response = self.client.get(url, data={'search': 'post2'})
        serializer_data = BikesSerializer(post, many=True).data
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(serializer_data, response.data['results'])


class RelationTestCase(APITestCase):
    """Тест отношения пользователей к постам"""

    def setUp(self):
        """Данные для тестирования"""

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create(username='test_username')
        self.user2 = self.user_model.objects.create(username='test_username2')
        self.c_1 = Category.objects.create(name='cat1')
        self.b_1 = Bike.published.create(title='post1', content='cont1', cat_id=self.c_1.id,
                                         auth_user=self.user)
        self.b_2 = Bike.published.create(title='post2', content='cont2', cat_id=self.c_1.id)

    def test_likes(self):
        """Тест лайков"""

        path = reverse('userpostrelation-detail', args=(self.b_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(path, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        relation = UserPostRelation.objects.get(auth_user=self.user,
                                                bike=self.b_1)
        self.assertTrue(relation.like)

    def test_rate(self):
        """Тест установки рейтинга"""
        path = reverse('userpostrelation-detail', args=(self.b_1.id,))
        data = {
            'rate': 5,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(path, data=json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        relation = UserPostRelation.objects.get(auth_user=self.user,
                                                bike=self.b_1)
        self.assertEqual(5, relation.rate)

    def test_rate_wrong(self):
        """Тест неверного значения рейтинга"""

        path = reverse('userpostrelation-detail', args=(self.b_1.id,))
        data = {
            'rate': 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(path, data=json_data,
                                     content_type='application/json')
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code, response.data)


class SerializerTestCase(TestCase):
    """Тестирование сериализатора"""

    def setUp(self):
        """Данные для тестирования"""

        self.user_model = get_user_model()
        self.user1 = self.user_model.objects.create(username='test_username1')
        self.user2 = self.user_model.objects.create(username='test_username2')
        self.user3 = self.user_model.objects.create(username='test_username3')

        self.c_1 = Category.objects.create(name='cat1')
        tag1 = Tags.objects.create(tag='Тег1')
        tag2 = Tags.objects.create(tag='Тег2')
        self.b_1 = Bike.published.create(title='post_1', content='post_1_content', cat_id=self.c_1.id,
                                         auth_user=self.user1)
        self.b_2 = Bike.published.create(title='post_2', content='post_2_content', cat_id=self.c_1.id)
        self.b_2.tags.add(tag1, tag2)

        UserPostRelation.objects.create(auth_user=self.user1, bike=self.b_1, like=True,
                                        rate=3)
        UserPostRelation.objects.create(auth_user=self.user2, bike=self.b_1, like=True,
                                        rate=4)
        UserPostRelation.objects.create(auth_user=self.user3, bike=self.b_1, like=True,
                                        rate=5)

        UserPostRelation.objects.create(auth_user=self.user3, bike=self.b_2, like=True,
                                        rate=1)
        UserPostRelation.objects.create(auth_user=self.user3, bike=self.b_2, like=True,
                                        rate=2)
        UserPostRelation.objects.create(auth_user=self.user3, bike=self.b_2, like=False)

    def test_ok(self):
        """Тест на успешную сериализацию"""

        posts = Bike.objects.all().annotate(
            count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
            rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')

        data = BikesSerializer(posts, many=True).data
        expected_data = [
            {
                'title': 'post_2',
                'slug': 'post_2',
                'content': 'post_2_content',
                'created': self.b_2.created.replace(tzinfo=None).isoformat() + 'Z',
                'modified': self.b_2.modified.replace(tzinfo=None).isoformat() + 'Z',
                'cat': self.b_2.cat.name,
                'tags': [1, 2],
                'is_published': 1,
                'count_likes': 2,
                'rating': '1.50'

            },
            {
                'title': 'post_1',
                'slug': 'post_1',
                'content': 'post_1_content',
                'created': self.b_1.created.replace(tzinfo=None).isoformat() + 'Z',
                'modified': self.b_1.modified.replace(tzinfo=None).isoformat() + 'Z',
                'cat': self.b_1.cat.name,
                'tags': [],
                'is_published': 1,
                'count_likes': 3,
                'rating': '4.00'
            },
        ]
        self.assertEqual(expected_data, data)
