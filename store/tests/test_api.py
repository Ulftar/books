from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def test_get(self):
        # Создаем с помощью ОРМ тестовый список книг
        book_1 = Book.objects.create(name='Test book 1', price=25)
        book_2 = Book.objects.create(name='Test book 2', price=55)
        # Тестируем ответ от url localhost/book/
        url = reverse('book-list')
        response = self.client.get(url)
        # Передаем список объектов для сравнения, аргумент many для сериализации каждого элемента списка
        serializer_data = BooksSerializer([book_1, book_2], many=True).data
        self.assertEqual(serializer_data, response.data)
        # Тестируем код ответа сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
