"""
# Collection Router
"""


# Library Imports
# #############################################################################


from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers
from collections import namedtuple


# App Imports
# #############################################################################


from api.views import (
    CollectionViewSet,
    ItemViewSet,
    UserViewSet,
    UserSearchView,
)


# Router Setup
# #############################################################################


collection_router = routers.DefaultRouter(trailing_slashes=False)

collection_router.register(r'collections', CollectionViewSet)
collection_router.register(r'items', ItemViewSet)


collection_router.register(r'users', UserViewSet)
collection_router.register("users/search", UserSearchView, base_name="user-search")

# EOF
# #############################################################################
