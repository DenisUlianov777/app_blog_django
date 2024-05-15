from django.conf import settings


class DataMixin:
    """Миксин для классов представлений, использующих встроенную пагинацию и дополнительный контекст"""

    paginate_by = 1
    extra_context = {'default_img': settings.DEFAULT_POST_IMAGE}


def get_initial_rate(self):
    from bike_app.models import UserPostRelation

    if self.request.user.is_authenticated:
        return UserPostRelation.objects.filter(
            auth_user=self.request.user,
            bike=self.object
        ).values_list('rate', flat=True).first()
    return None
