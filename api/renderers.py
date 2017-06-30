import os
from collections import OrderedDict

from django.utils import encoding, six
from rest_framework import relations
from rest_framework.settings import api_settings

from rest_framework_json_api import utils
from rest_framework_json_api.renderers import JSONRenderer
from api.base.serializers import RelationshipField

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")


class CustomJSONRenderer(JSONRenderer):
    """
    Override rest framework json api JSONRenderer to remove embedded data from related
    resources and to handle the custom RelationshipField.
    """

    @staticmethod
    def extract_relationships(fields, resource, resource_instance):
        data = JSONRenderer.extract_relationships(fields, resource, resource_instance)
        # Do not alter RelationshipFields, which handle JSON API formatting
        for field_name, field in six.iteritems(fields):
            if isinstance(field, RelationshipField):
                data.update({field_name: resource.get(field_name)})
        # Remove embedded relationship data
        for field in data:
            if isinstance(field, RelationshipField):
                ret = {}
                for key in data[field]:
                    if key != 'data':
                        ret[key] = data[field][key]
                data[field] = ret
        return utils.format_keys(data)

    @staticmethod
    def build_json_resource_obj(fields, resource, resource_instance, resource_name):
        resource_data = [
            ('type', resource_name),
            ('id', encoding.force_text(resource_instance.pk) if resource_instance else None),
            ('attributes', JSONRenderer.extract_attributes(fields, resource)),
        ]
        # Use CustomJSONRenderer.extract_relationships, which removes embedded data
        relationships = CustomJSONRenderer.extract_relationships(fields, resource, resource_instance)
        if relationships:
            resource_data.append(('relationships', relationships))
        # Add 'self' link if field is present and valid
        if api_settings.URL_FIELD_NAME in resource and \
                isinstance(fields[api_settings.URL_FIELD_NAME], relations.RelatedField):
            resource_data.append(('links', {'self': resource[api_settings.URL_FIELD_NAME]}))
        return OrderedDict(resource_data)
