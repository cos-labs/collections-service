from haystack import indexes
from api.models import Collection, Meeting, Item, CollectionBase
from django.contrib.auth.models import User


class CollectionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='title')
    created_by = indexes.CharField(model_attr='created_by')

    def get_model(self):
        return Collection

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated
        """
        return self.get_model().objects.all()


class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='title')
    created_by = indexes.CharField(model_attr='created_by')

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated
        """
        return self.get_model().objects.all()


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated
        """
        return self.get_model().objects.all()


class MeetingIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='title')
    created_by = indexes.CharField(model_attr='created_by')

    def get_model(self):
        return Meeting

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated
        """
        return self.get_model().objects.all()


class CollectionBaseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return CollectionBase

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated
        """
        return self.get_model().objects.all()
