from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Six offers per page, matching the frontend's page size."""

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
