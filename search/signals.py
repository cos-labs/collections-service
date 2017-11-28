from django.db import models
from haystack.signals import BaseSignalProcessor

from haystack.exceptions import NotHandled


#
class QueuedSignalProcessor(BaseSignalProcessor):
#     """
#     Allows for observing when saves/deletes fire & automatically updates the
#     search engine appropriately.
#     """
#
#     def setup(self):
#         # Naive (listen to all model saves).
#         models.signals.post_save.connect(self.handle_save)
#         models.signals.post_delete.connect(self.handle_delete)
#         # Efficient would be going through all backends & collecting all models
#         # being used, then hooking up signals only for those.
#
#     def teardown(self):
#         # Naive (listen to all model saves).
#         models.signals.post_save.disconnect(self.handle_save)
#         models.signals.post_delete.disconnect(self.handle_delete)
#         # Efficient would be going through all backends & collecting all models
#         # being used, then disconnecting signals only for those.
#
#     def handle_save(self, sender, instance, **kwargs):
#         """
#         Given an individual model instance, determine which backends the
#         update should be sent to & update the object on those backends.
#         """
#         using_backends = self.connection_router.for_write(instance=instance)
#
#         for using in using_backends:
#             try:
#                 index = self.connections[using].get_unified_index().get_index(sender)
#                 index.update_object(instance, using=using)
#             except NotHandled:
#                 # TODO: Maybe log it or let the exception bubble?
#                 pass
#
#     def handle_delete(self, sender, instance, **kwargs):
#         """
#         Given an individual model instance, determine which backends the
#         delete should be sent to & delete the object on those backends.
#         """
#         using_backends = self.connection_router.for_write(instance=instance)
#
#         for using in using_backends:
#             try:
#                 index = self.connections[using].get_unified_index().get_index(sender)
#                 index.remove_object(instance, using=using)
#             except NotHandled:
#                 # TODO: Maybe log it or let the exception bubble?
#                 pass
#
    pass
