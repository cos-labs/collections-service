"""
Collection Mixins
"""


# Library Imports
# #############################################################################


from django.db.models import ForeignKey
from django.contrib.postgres.fields import JSONField
from guardian.shortcuts import assign_perm


# App Imports
# #############################################################################


from collection.models import Collection
from tests import resources


# Models
# #############################################################################



# class CollectionUserMixin:
#
#     collection = ForeignKey(
#         "Collection",
#         blank=True,
#         null=True
#     )
#
#     def save(self, *args, **kwargs):
#         if not self.collection.pk:
#             self.collection = Collection()
#             self.collection.title = self.full_name + "'s Collection"
#             self.collection.description = "My Collection"
#             self.collection.owner = self
#             self.collection.save()
#             super().save(*args, **kwargs)
#             assign_perm("view_object", self, self._collection)
#         return self._collection
#
#
