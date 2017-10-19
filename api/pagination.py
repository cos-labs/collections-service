"""
# Pagination Classes

- LargeResultsSetPagination
"""


# Imports
# #############################################################################


from rest_framework_json_api import pagination


# Pagination Classes
# #############################################################################


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


# EOF
# #############################################################################
