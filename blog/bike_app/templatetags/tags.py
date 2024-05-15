from django import template
from django.db.models import Count

from bike_app.models import *

register = template.Library()


@register.inclusion_tag('bike_app/list_categories.html')
def show_categories(cat_selected=0):
    return {'cats': Category.objects.annotate(amount=Count("posts")).filter(amount__gt=0), 'cat_selected': cat_selected}


@register.inclusion_tag('bike_app/list_tags.html')
def show_tags():
    return {"tags": Tags.objects.annotate(amount=Count("posts")).filter(amount__gt=0)}
