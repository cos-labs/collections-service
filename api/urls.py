from django.conf.urls import url, include
import api.views

urlpatterns = [
    url(r'^$', api.views.api_root),
    url(r'^collections/$', api.views.CollectionList.as_view(), name='collection-list'),
    url(r'^collections/(?P<pk>\w+)/$', api.views.CollectionDetail.as_view(), name='collection-detail'),
    url(r'^collections/(?P<pk>\w+)/groups/$', api.views.CollectionGroupList.as_view(), name='collection-group-list'),
    url(r'^collections/(?P<pk>\w+)/groups/(?P<group_id>\w+)/$', api.views.GroupDetail.as_view(), name='collection-group-detail'),
    url(r'^collections/(?P<pk>\w+)/groups/(?P<group_id>\w+)/items/$', api.views.GroupItemList.as_view(), name='group-item-list'),
    url(r'^collections/(?P<pk>\w+)/groups/(?P<group_id>\w+)/items/(?P<item_id>\w+)/$', api.views.ItemDetail.as_view(), name='group-item-detail'),
    url(r'^collections/(?P<pk>\w+)/items/$', api.views.CollectionItemList.as_view(), name='collection-item-list'),
    url(r'^collections/(?P<pk>\w+)/items/(?P<item_id>\w+)/$', api.views.ItemDetail.as_view(), name='collection-item-detail'),

    url(r'^groups/$', api.views.GroupList.as_view(), name='group-list'),
    url(r'^groups/(?P<group_id>\w+)/$', api.views.GroupDetail.as_view(), name='group-detail'),

    url(r'^items/$', api.views.ItemList.as_view(), name='item-list'),
    url(r'^items/(?P<item_id>\w+)/$', api.views.ItemDetail.as_view(), name='item-detail'),

    url(r'^userinfo/$', api.views.CurrentUser.as_view(), name='current-user'),
    url(r'^users/$', api.views.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<user_id>\w+)/$', api.views.UserDetail.as_view(), name='user-detail'),

]
