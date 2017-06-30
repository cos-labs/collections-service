import re
from django.core.urlresolvers import resolve, reverse, NoReverseMatch
from django.core.exceptions import ImproperlyConfigured
from rest_framework.fields import SkipField
from rest_framework.fields import get_attribute as get_nested_attributes
from rest_framework import serializers


def format_relationship_links(related_link=None, self_link=None, rel_meta=None, self_meta=None):
    """
    Properly handles formatting of self and related links according to JSON API.

    Removes related or self link, if none.
    """

    ret = {'links': {}}

    if related_link:
        ret['links'].update({
            'related': {
                'href': related_link or {},
                'meta': rel_meta or {}
            }
        })

    if self_link:
        ret['links'].update({
            'self': {
                'href': self_link or {},
                'meta': self_meta or {}
            }
        })

    return ret


def _tpl(val):
    """Return value within ``< >`` if possible, else return ``None``."""
    _tpl_pattern = re.compile(r'\s*<\s*(\S*)\s*>\s*')
    match = _tpl_pattern.match(val)
    if match:
        return match.groups()[0]
    return None


class RelationshipField(serializers.HyperlinkedIdentityField):
    """
    Adapted from https://github.com/CenterForOpenScience/osf.io/blob/develop/api/base/serializers.py#L354

    RelationshipField that permits the return of both self and related links, along with optional
    meta information. ::

        children = RelationshipField(
            related_view='nodes:node-children',
            related_view_kwargs={'node_id': '<pk>'},
            self_view='nodes:node-node-children-relationship',
            self_view_kwargs={'node_id': '<pk>'},
            related_meta={'count': 'get_node_count'}
        )

    The lookup field must be surrounded in angular brackets to find the attribute on the target. Otherwise, the lookup
    field will be returned verbatim. ::

        wiki_home = RelationshipField(
            related_view='addon:addon-detail',
            related_view_kwargs={'node_id': '<_id>', 'provider': 'wiki'},
        )

    '_id' is enclosed in angular brackets, but 'wiki' is not. 'id' will be looked up on the target, but 'wiki' will not.
     The serialized result would be '/nodes/abc12/addons/wiki'.

    Field can handle nested attributes: ::

        wiki_home = RelationshipField(
            related_view='wiki:wiki-detail',
            related_view_kwargs={'node_id': '<_id>', 'wiki_id': '<wiki_pages_current.home>'}
        )
    """
    json_api_link = True  # serializes to a links object

    def __init__(self, related_view=None, related_view_kwargs=None, self_view=None, self_view_kwargs=None,
                 self_meta=None, related_meta=None, always_embed=False, **kwargs):
        related_view = related_view
        self_view = self_view
        related_kwargs = related_view_kwargs
        self_kwargs = self_view_kwargs
        self.views = {'related': related_view, 'self': self_view}
        self.view_kwargs = {'related': related_kwargs, 'self': self_kwargs}
        self.related_meta = related_meta
        self.self_meta = self_meta
        self.always_embed = always_embed

        assert (related_view is not None or self_view is not None), 'Self or related view must be specified.'
        if related_view:
            assert related_kwargs is not None, 'Must provide related view kwargs.'
            if not callable(related_kwargs):
                assert isinstance(related_kwargs,
                                  dict), "Related view kwargs must have format {'lookup_url_kwarg: lookup_field}."
        if self_view:
            assert self_kwargs is not None, 'Must provide self view kwargs.'
            assert isinstance(self_kwargs, dict), "Self view kwargs must have format {'lookup_url_kwarg: lookup_field}."

        view_name = related_view
        if view_name:
            lookup_kwargs = related_kwargs
        else:
            view_name = self_view
            lookup_kwargs = self_kwargs
        if kwargs.get('lookup_url_kwarg', None):
            lookup_kwargs = kwargs.pop('lookup_url_kwarg')
        super(RelationshipField, self).__init__(view_name, lookup_url_kwarg=lookup_kwargs, **kwargs)

        # Allow a RelationshipField to be modified if explicitly set so
        if kwargs.get('read_only') is not None:
            self.read_only = kwargs['read_only']

    def resolve(self, resource, field_name, request):
        """
        Resolves the view when embedding.
        """
        lookup_url_kwarg = self.lookup_url_kwarg
        if callable(lookup_url_kwarg):
            lookup_url_kwarg = lookup_url_kwarg(getattr(resource, field_name))

        kwargs = {attr_name: self.lookup_attribute(resource, attr) for (attr_name, attr) in lookup_url_kwarg.items()}
        # kwargs.update({'version': request.parser_context['kwargs']['version']})

        view = self.view_name
        if callable(self.view_name):
            view = view(getattr(resource, field_name))
        return resolve(
            reverse(
                view,
                kwargs=kwargs
            )
        )

    def get_meta_information(self, meta_data, value):
        """
        For retrieving meta values, otherwise returns {}
        """
        meta = {}
        # for key in meta_data or {}:
        #     meta[key] = website_utils.rapply(meta_data[key], _url_val, obj=value, serializer=self.parent, request=self.context['request'])
        return meta

    def lookup_attribute(self, obj, lookup_field):
        """
        Returns attribute from target object unless attribute surrounded in angular brackets where it returns the lookup field.

        Also handles the lookup of nested attributes.
        """
        bracket_check = _tpl(lookup_field)
        if bracket_check:
            source_attrs = bracket_check.split('.')
            # If you are using a nested attribute for lookup, and you get the attribute wrong, you will not get an
            # error message, you will just not see that field. This allows us to have slightly more dynamic use of
            # nested attributes in relationship fields.
            try:
                return_val = get_nested_attributes(obj, source_attrs)
            except KeyError:
                return None
            return return_val

        return lookup_field

    def kwargs_lookup(self, obj, kwargs_dict):
        """
        For returning kwargs dictionary of format {"lookup_url_kwarg": lookup_value}
        """
        if callable(kwargs_dict):
            kwargs_dict = kwargs_dict(obj)

        kwargs_retrieval = {}
        for lookup_url_kwarg, lookup_field in kwargs_dict.items():
            try:
                lookup_value = self.lookup_attribute(obj, lookup_field)
            except AttributeError as exc:
                raise AssertionError(exc)
            if lookup_value is None:
                return None
            kwargs_retrieval[lookup_url_kwarg] = lookup_value
        return kwargs_retrieval

    # Overrides HyperlinkedIdentityField
    def get_url(self, obj, view_name, request, format):
        urls = {}
        for view_name, view in self.views.items():
            if view is None:
                urls[view_name] = {}
            else:
                kwargs = self.kwargs_lookup(obj, self.view_kwargs[view_name])
                if kwargs is None:
                    urls[view_name] = {}
                else:
                    if callable(view):
                        view = view(getattr(obj, self.field_name))
                    urls[view_name] = self.reverse(view, kwargs=kwargs, request=request, format=format)

        if not urls['self'] and not urls['related']:
            urls = None
        return urls

    # Overrides HyperlinkedIdentityField
    def to_representation(self, value):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        assert request is not None, (
            '`%s` requires the request in the serializer'
            " context. Add `context={'request': request}` when instantiating "
            'the serializer.' % self.__class__.__name__
        )

        # By default use whatever format is given for the current context
        # unless the target is a different type to the source.
        #
        # Eg. Consider a HyperlinkedIdentityField pointing from a json
        # representation to an html property of that representation...
        #
        # '/snippets/1/' should link to '/snippets/1/highlight/'
        # ...but...
        # '/snippets/1/.json' should link to '/snippets/1/highlight/.html'
        if format and self.format and self.format != format:
            format = self.format

        # Return the hyperlink, or error if incorrectly configured.
        try:
            url = self.get_url(value, self.view_name, request, format)
        except NoReverseMatch:
            msg = (
                'Could not resolve URL for hyperlinked relationship using '
                'view name "%s". You may have failed to include the related '
                'model in your API, or incorrectly configured the '
                '`lookup_field` attribute on this field.'
            )
            if value in ('', None):
                value_string = {'': 'the empty string', None: 'None'}[value]
                msg += (
                    ' WARNING: The value of the field on the model instance '
                    "was %s, which may be why it didn't match any "
                    'entries in your URL conf.' % value_string
                )
            raise ImproperlyConfigured(msg % self.view_name)

        if url is None:
            raise SkipField

        related_url = url['related']
        related_meta = self.get_meta_information(self.related_meta, value)
        self_url = url['self']
        self_meta = self.get_meta_information(self.self_meta, value)
        return format_relationship_links(related_url, self_url, related_meta, self_meta)