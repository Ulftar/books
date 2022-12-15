from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    # Устанавливаем фильтры
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Проверка аутентификации
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    # Фильтрация по цене
    filterset_fields = ['price']
    # Поиск по имени и автору
    search_fields = ['name', 'author_name']
    # Сортировка по цене и автору
    ordering_fields = ['price', 'author_name']

    # Добавляем права овнера при создании книги
    def perform_create(self, serializer):
        # Создавать книгу может только авторизованный пользователь, поэтому добаляем user
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


# Представление системы рейтов
class UserBooksRelationView(UpdateModelMixin, GenericViewSet):
    # Предоставление только аутентифицированным пользователям
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'


# Аутентификация ГитХаб
def auth(request):
    return render(request, 'oauth.html')
