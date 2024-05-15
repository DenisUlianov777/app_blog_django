# Blog Web Application с использованием следующих технологий:

<img src="https://img.shields.io/badge/Python-4169E1?style=for-the-badge"/> <img src="https://img.shields.io/badge/Django-008000?style=for-the-badge"/> <img src="https://img.shields.io/badge/DRF-800000?style=for-the-badge"/> <img src="https://img.shields.io/badge/Docker-00BFFF?style=for-the-badge"/> <img src="https://img.shields.io/badge/PostgreSQL-87CEEB?style=for-the-badge"/> <img src="https://img.shields.io/badge/Nginx-67c273?style=for-the-badge"/> <img src="https://img.shields.io/badge/Gunicorn-06bd1e?style=for-the-badge"/> <img src="https://img.shields.io/badge/Redis-800000?style=for-the-badge"/> <img src="https://img.shields.io/badge/Celery-06bd1e?style=for-the-badge"/> <img src="https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white"/> <img src="https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white"/>

# Как запустить проект:

*Клонировать репозиторий:*
```
https://github.com/DenisUlianov777/app_blog_django.git
```
```
cd app_blog_django/
```

Cоздать .env.prod файл.
Например:
```
DEBUG=True
SECRET_KEY='django-insecure-dx(8kq_$'
ALLOWED_HOSTS='127.0.0.1'
INTERNAL_IPS='127.0.0.1'
CSRF_TRUSTED_ORIGINS='http://127.0.0.1'

DB_ENGINE=django.db.backends.postgresql
DB_NAME=blog
DB_USER=admin
DB_PASSWORD=admin
DB_HOST=database
DB_PORT=5432
DATABASE=postgres

CACHE_BACKEND='django.core.cache.backends.redis.RedisCache'
CACHE_LOCATION='redis://redis:6378/1'

CELERY_BROKER_URL='redis://redis:6378/0'
CELERY_RESULT_BACKENDS='redis://redis:6378/0'

SOCIAL_AUTH_GITHUB_KEY='fbfdbfbr3'
SOCIAL_AUTH_GITHUB_SECRET='b43brgehehdfhgdg'

EMAIL_HOST='smtp.yandex.ru'
EMAIL_PORT=465
EMAIL_HOST_USER='blog@yandex.ru'
EMAIL_HOST_PASSWORD='ozjydxlmpgdgpxch'
EMAIL_USE_SSL=True
```

*Собрать и запустить Docker-контейнеры:*
```
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
```


*Теперь проект доступен по адресу:*
```
http://127.0.0.1:80
```

*Документация для API:*
```
/api/v1/schema/redoc/
```

```
/api/v1/rschema/swagger-ui/
```
