from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    # Параметры создателя книги
    # ForeignKey - связь один уо многим, у одного юзера может быть создано несколько книг
    # on_delete - параметр, отвечающий за дествия после удаления юзера, книги могут существовать дальше
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True)

    # Настраиваем отображение книг в админке, ID: название.
    def __str__(self):
        return f'Id {self.id}: {self.name}'