from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book, UserBookRelation


# Регистрация модели книги в админке
@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass


# Регистрация модели рейтов в админке
@admin.register(UserBookRelation)
class UserBookRelationAdmin(ModelAdmin):
    pass
