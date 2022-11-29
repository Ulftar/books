from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book


# Регистрация модели книги в админке
@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass
