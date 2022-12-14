import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователся
        self.user = User.objects.create(username='test_username')
        # Создаем с помощью ОРМ тестовый список книг
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 1',
                                          owner=self.user)
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
        response = self.client.get(url, data={'price': 55})
        serializer_data = BooksSerializer([self.book_2,
                                           self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # Тест поиска
    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book_1,
                                           self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # Тест сортировки
    def test_get_order(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        serializer_data = BooksSerializer([self.book_1,
                                           self.book_3,
                                           self.book_2], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # Тест запроса на создание книги
    def test_create(self):
        # Смотрим текущее количество книг в базе
        self.assertEqual(3, Book.objects.all().count())
        # Тестируем ответ от url localhost/book/
        url = reverse('book-list')
        # Данные для создания книги
        data = {
            'name': 'Программирование на Пайтоне',
            'price': 150,
            'author_name': 'Марк Саммерфилд'
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Отправляем пост запрос
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # Смотрим количество книг выполнения запроса
        self.assertEqual(4, Book.objects.all().count())
        # Сравниваем что пользователь стал владельцем книги при создании
        self.assertEqual(self.user, Book.objects.last().owner)

    # Тест запроса на изменение книги
    def test_update(self):
        # Указываем айди объекта для запроса. Чтобы урл содержал в себе айди указываем book-detail
        url = reverse('book-detail', args=(self.book_1.id,))
        # Данные для изменения книги
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Отправляем пут запрос
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        # Проверяем код ответа от сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Пересоздаем объект в базе данных для действительного изменения цены
        self.book_1.refresh_from_db()
        # Проверяем что цена действительно изменилась
        self.assertEqual(575, self.book_1.price)

    # Тест негативного сценария апдейта
    def test_update_not_owner(self):
        # Создаем пользователся
        self.user2 = User.objects.create(username='test_username2')
        # Указываем айди объекта для запроса. Чтобы урл содержал в себе айди указываем book-detail
        url = reverse('book-detail', args=(self.book_1.id,))
        # Данные для изменения книги
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Авторизуем юзера, не владельца книги
        self.client.force_login(self.user2)
        # Отправляем пут запрос
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        # Проверка ответа от сервера
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        # Проверяем код ответа от сервера
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # Пересоздаем объект в базе данных для действительного изменения цены
        self.book_1.refresh_from_db()
        # Проверяем что цена не изменилась, так как у не овнера нет прав на изменение
        self.assertEqual(25, self.book_1.price)

    # Тест апдейта персоналом компании
    def test_update_not_owner_but_staff(self):
        # Создаем пользователся
        self.user2 = User.objects.create(username='test_username2',
                                         is_staff=True)
        # Указываем айди объекта для запроса. Чтобы урл содержал в себе айди указываем book-detail
        url = reverse('book-detail', args=(self.book_1.id,))
        # Данные для изменения книги
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Авторизуем юзера, не владельца книги
        self.client.force_login(self.user2)
        # Отправляем пут запрос
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        # Проверяем код ответа от сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Пересоздаем объект в базе данных для действительного изменения цены
        self.book_1.refresh_from_db()
        # Проверяем что цена не изменилась, так как у не овнера нет прав на изменение
        self.assertEqual(575, self.book_1.price)

    # Тест запроса на удаление книги
    def test_delete(self):
        # Смотрим текущее количество книг в базе
        self.assertEqual(3, Book.objects.all().count())
        # Указываем айди объекта для запроса. Чтобы урл содержал в себе айди указываем book-detail
        url = reverse('book-detail', args=(self.book_1.id,))
        # Данные для удаления книги
        data = {
            'name': self.book_1.name,
            'price': self.book_1.price,
            'author_name': self.book_1.author_name
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Отправляем пост запрос
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        # Проверяем код ответа от сервера
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        # Смотрим количество книг выполнения запроса
        self.assertEqual(2, Book.objects.all().count())

    # Тест негативного сценария удаления
    def test_delete_not_owner(self):
        # Создаем пользователся
        self.user2 = User.objects.create(username='test_username2')
        # Смотрим текущее количество книг в базе
        self.assertEqual(3, Book.objects.all().count())
        # Указываем айди объекта для запроса. Чтобы урл содержал в себе айди указываем book-detail
        url = reverse('book-detail', args=(self.book_1.id,))
        # Данные для удаления книги
        data = {
            'name': self.book_1.name,
            'price': self.book_1.price,
            'author_name': self.book_1.author_name
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)
        # Насильно авторизовываемся
        self.client.force_login(self.user2)
        # Отправляем пост запрос
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        # Проверка ответа от сервера
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        # Проверяем код ответа от сервера
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # Смотрим количество книг выполнения запроса
        self.assertEqual(3, Book.objects.all().count())


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create(username='test_username', )
        self.user2 = User.objects.create(username='test_username2', )
        # Создаем с помощью ОРМ тестовый список книг
        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                          author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                          author_name='Author 5')

    # Тест запроса
    def test_like(self):
        # Тестируем ответ от url localhost/book_relation/
        # Указываем айди объекта для запроса.
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'like': True,
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)

        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Обновляем данные модели, используем patch, т.к. обновляем один элемент
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        # Тестируем код ответа сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Берем данные из бази
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        # Проверяем наличие лайка у релейшена, по умолчанию его нет (false)
        self.assertTrue(relation.like)

        # Проверяем добавление в закладки
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)

        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)


    # Тест рейта
    def test_rate(self):
        # Тестируем ответ от url localhost/book_relation/
        # Указываем айди объекта для запроса.
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'rate': 3,
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)

        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Обновляем данные модели, используем patch, т.к. обновляем один элемент
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        # Тестируем код ответа сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Берем данные из базы
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        # Проверяем рейт
        self.assertEqual(3, relation.rate)

    def test_rate(self):
        # Тестируем ответ от url localhost/book_relation/
        # Указываем айди объекта для запроса.
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'rate': 3,
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)

        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Обновляем данные модели, используем patch, т.к. обновляем один элемент
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        # Тестируем код ответа сервера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Берем данные из базы
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        # Проверяем рейт
        self.assertEqual(3, relation.rate)

    # Негативный тест рейта
    def test_rate_wrong(self):
        # Тестируем ответ от url localhost/book_relation/
        # Указываем айди объекта для запроса.
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'rate': 6,
        }
        # Преобразуем данные в json
        json_data = json.dumps(data)

        # Насильно авторизовываемся
        self.client.force_login(self.user)
        # Обновляем данные модели, используем patch, т.к. обновляем один элемент
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        # Тестируем код ответа сервера. Третим аргументом задаем сообщение, если проверка не прошла
        self.assertEqual(status.HTTP_200_OK, response.status_code, response.data)
        # Берем данные из базы
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        # Проверяем рейт
        self.assertEqual(3, relation.rate)
