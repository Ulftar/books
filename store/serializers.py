from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


# API для книг
class BooksSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


# API для системы рейтов
class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')
