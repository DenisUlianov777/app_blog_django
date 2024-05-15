from django.db.models import Avg, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bike_app.models import *

from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import BikesSerializer, UserPostRelationSerializer


class BikesViewSet(viewsets.ModelViewSet):
    """Представление для работы с объектами Bike"""

    queryset = Bike.objects.all().annotate(
        count_likes=Count('userpostrelation', filter=Q(userpostrelation__like=True)),
        rating=Avg('userpostrelation__rate')).select_related('cat').order_by('-created')
    serializer_class = BikesSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['$title', '$content', '$cat__name']
    ordering_fields = ['created', 'modified']

    @action(methods=['get'], detail=True)
    def tags(self, request, pk: int = None) -> Response:
        """Возвращает категорию по id"""

        tag = Tags.objects.get(pk=pk)
        return Response({'tag': tag.tag})


class UserPostRelationView(UpdateModelMixin, GenericViewSet):
    """Представление для работы с отношениями пользователя к постам"""

    queryset = UserPostRelation.objects.all()
    serializer_class = UserPostRelationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'bike_id'

    def get_object(self) -> UserPostRelation:
        """Получает или создает объект UserPostRelation для текущего пользователя и указанного поста"""

        obj, _ = UserPostRelation.objects.get_or_create(auth_user=self.request.user,
                                                        bike_id=self.kwargs['bike_id'])
        return obj
