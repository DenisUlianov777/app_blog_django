from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.db.models.functions import Length
from django.utils.safestring import mark_safe

from .models import *


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'content', 'photo', 'post_photo', 'is_published', 'cat', 'tags', 'auth_user')
    list_display = ('id', 'title', 'created', 'post_photo', 'is_published', 'cat', 'num_char')  # поля списка постов
    list_display_links = ('id', 'title')
    readonly_fields = ['post_photo', 'slug']
    search_fields = ('title', 'cat__name')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created', 'cat__name')
    filter_horizontal = ['tags']
    list_per_page = 10
    save_on_top = True
    actions = ['set_published', 'set_unpublished']

    @admin.display(description='Изображение', ordering='')
    def post_photo(self, bike: Bike):
        if bike.photo:
            return mark_safe(f"<img src='{bike.photo.url}' width=50>")
        return 'Нет фото'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(len_content=Length('content'))

    @admin.display(description='Кол-во символов', ordering='len_content')
    def num_char(self, bike: Bike):
        return f'{bike.len_content} символов'

    @admin.action(description="Опубликовать")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Bike.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записи(ей).")

    @admin.action(description="Снять с публикации")
    def set_unpublished(self, request, queryset):
        count = queryset.update(is_published=Bike.Status.DRAFT)
        self.message_user(request, f"{count} записи(ей) сняты с публикации!", messages.WARNING)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class TagsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("tag",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(UserPostRelation)
