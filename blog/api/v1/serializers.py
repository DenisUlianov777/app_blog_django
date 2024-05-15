from rest_framework import serializers

from bike_app.models import *


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category"""

    class Meta:
        model = Category
        fields = '__all__'


class BikesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Bike"""

    auth_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    count_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Bike
        ordering = ['-created']
        fields = ('title', 'slug', 'content', 'created', 'modified', 'cat', 'tags', 'is_published', 'count_likes',
                  'rating', 'auth_user')

    def to_representation(self, instance):
        """Вывод названия категории вместо id"""

        rep = super().to_representation(instance)
        rep['cat'] = CategorySerializer(instance.cat).data['name']
        return rep


class UserPostRelationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserPostRelation"""

    class Meta:
        model = UserPostRelation
        fields = ('bike', 'like', 'rate')
