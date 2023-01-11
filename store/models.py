from django.contrib.auth.models import User
from django.db import models


# Модель книги
class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    # Параметры создателя книги
    # ForeignKey - связь один уо многим, у одного юзера может быть создано несколько книг
    # on_delete - параметр, отвечающий за дествия после удаления юзера, книги могут существовать дальше
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='my_books')
    # Читатели, отношение many to many, у книги может быть много читателей
    # В директиве trough прописываем нашу модель отношений
    # Задаем разные related names, потому что владелец и читатели ссылаются на юзера
    readers = models.ManyToManyField(User, through='UserBookRelation',
                                     related_name='books')

    # Настраиваем отображение книг в админке, ID: название.
    def __str__(self):
        return f'Id {self.id}: {self.name}'


# Модель лайков
class UserBookRelation(models.Model):
    # Первый элемент вложенного кортежа - значение рейтинга, которое хранится в базе
    # Второй - значение рейтинга, которое мы отрисуем
    RATE_CHOICES = (
        (1, 'Нормально'),
        (2, 'Неплохо'),
        (3, 'Хорошо'),
        (4, 'Отлично'),
        (5, 'Замечательно')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    # Рейтинг может быть пустым, добавляем null=True
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    # Настраиваем отображение рейтов в админке
    def __str__(self):
        return f'{self.user.username}: {self.book.name}, Rate: {self.rate}'
