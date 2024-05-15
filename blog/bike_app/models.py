from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from unidecode import unidecode


class PublishedManager(models.Manager):
    """Менеджер для получения только опубликованных постов"""

    def get_queryset(self):
        return super().get_queryset().filter(is_published=Bike.Status.PUBLISHED)


class Bike(TimeStampedModel, models.Model):
    """Модель для хранения постов"""

    class Status(models.IntegerChoices):
        """Статусы поста"""
        DRAFT = 0, 'Не опубликовано'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, unique=True, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    photo = models.ImageField(upload_to="pictures/%Y/%m/%d/", blank=True, verbose_name="Фото")
    is_published = models.IntegerField(choices=Status.choices, default=Status.PUBLISHED, verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name="Категории")
    tags = models.ManyToManyField("Tags", blank=True, related_name='posts', verbose_name="Теги")
    auth_user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True,
                                  default=None, verbose_name="Автор")
    readers = models.ManyToManyField(get_user_model(), related_name='readers', through='UserPostRelation')

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения объекта с добавленем значения в поле slug"""

        transliterated_title = unidecode(self.title)
        self.slug = slugify(transliterated_title)
        super().save(*args, **kwargs)
        cache.delete('home_cache')

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete('home_cache')


class Category(models.Model):
    """Модель для хранения категорий"""

    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")  # AutoSlugField

    def __str__(self):
        return self.name

    def get_absolute_url(self):  # lesson 8
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'
        ordering = ['id']

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения объекта с добавленем значения в поле slug"""

        transliterated_name = unidecode(self.name)
        self.slug = slugify(transliterated_name)
        super().save(*args, **kwargs)



class Tags(models.Model):
    """Модель для хранения тегов"""

    tag = models.CharField(max_length=100, db_index=True, verbose_name="Название тэга")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения объекта с добавленем значения в поле slug"""

        transliterated_tag = unidecode(self.tag)
        self.slug = slugify(transliterated_tag)
        super().save(*args, **kwargs)



class UserPostRelation(models.Model):
    """Модель для хранения отношений пользователей и постов"""

    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible')
    )
    auth_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь')
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, verbose_name='Пост')
    like = models.BooleanField(default=False, verbose_name='Like')
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, blank=True, null=True, verbose_name='Рэйтинг')

    def __str__(self):
        return f' {self.auth_user.username}: {self.bike.title}, rate {self.rate}'

    class Meta:
        verbose_name = 'Оценки'
        verbose_name_plural = 'Оценки'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('home_cache')

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete('home_cache')
