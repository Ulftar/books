from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        # Создаем с помощью ОРМ тестовый список книг
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 1')
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 5')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55,
                                          author_name='Author 2')


    # Тест запроса
    def test_get(self):
        # Тестируем ответ от url localhost/book/
        url = reverse('book-list')
        response = self.client.get(url)
        # Передаем список объектов для сравнения, аргумент many для сериализации каждого элемента списка
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        # Тестируем код ответа сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)


    # Тест фильтров
    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book_1,
                                           self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
