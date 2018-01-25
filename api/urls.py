from django.conf.urls import url, include
import api.views
from rest_framework.routers import DefaultRouter

from api.routers import collection_router

router = DefaultRouter()
router.register("collections/search", api.views.CollectionSearchView, base_name="collection-search")
router.register("items/search", api.views.ItemSearchView, base_name="item-search")
router.register("users/search", api.views.UserSearchView, base_name="user-search")

urlpatterns = [

    url(r'^$', api.views.api_root),
    url(r'', include(collection_router.urls)),
    url(r'', include(router.urls)),

]
