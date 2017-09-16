# -*- coding: utf-8 -*-
"""Workflow Routers"""


from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers
from collections import namedtuple

from workflow import views


Route = namedtuple('Route', ['url', 'mapping', 'name', 'initkwargs'])
DynamicDetailRoute = namedtuple('DynamicDetailRoute', ['url', 'name', 'initkwargs'])
DynamicListRoute = namedtuple('DynamicListRoute', ['url', 'name', 'initkwargs'])


class NestedQueryableRecordRouter(routers.NestedDefaultRouter):

    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route that has no pk.
        Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'retrieve',
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_urls(self):
        """
        Generate the list of URL patterns, including a default root view
        for the API, and appending `.json` style format suffixes.
        """

        urls = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                # route.mapping doesn't always exist and raises an exception
                try:
                    mapping = self.get_method_map(viewset, route.mapping)
                    if not mapping:
                        continue
                except:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                #   controlled by project's urls.py and the router is in an app,
                #   so a slash in the beginning will (A) cause Django to give
                #   warnings and (B) generate URLS that will require using '//'.
                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]

                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                urls.append(url(regex, view, name=name))

        if self.include_root_view:
            if self.schema_title:
                view = self.get_schema_root_view(api_urls=urls)
            else:
                view = self.get_api_root_view(api_urls=urls)
            root_url = url(r'^$', view, name=self.root_view_name)
            urls.append(root_url)

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        return urls


workflow_router = routers.DefaultRouter(trailing_slash=False)

workflow_router.register(r'workflows', views.Workflow)
workflow_router.register(r'sections', views.Section)
workflow_router.register(r'widgets', views.Widget)
workflow_router.register(r'parameter-aliases', views.ParameterAlias)
workflow_router.register(r'parameter-stubs', views.ParameterStub)
workflow_router.register(r'parameters', views.Parameter)
workflow_router.register(r'cases', views.Case)

case_router = NestedQueryableRecordRouter(workflow_router, r'cases', lookup='case', trailing_slash=False)
case_router.register(r'parameters', views.Parameter, base_name='case-parameters')
case_router.register(r'parameter-aliases', views.ParameterAlias, base_name='case-parameter-aliases')
