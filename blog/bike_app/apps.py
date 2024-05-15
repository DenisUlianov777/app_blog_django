from django.apps import AppConfig


class Bike_AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # зачем то было в комментарии
    name = "bike_app"
    verbose_name = 'Веломир'

