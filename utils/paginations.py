from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # https://.../api/friendships/1/followers/?page=3&size=10

    # Default page_size
    page_size = 20
    # If the default page_size_query_param is None, it won't allow client
    # to set page_size. page_size_query_param = 'size' means that client
    # can set different page sizes for different situations (e.g. web vs
    # mobile requests)
    page_size_query_param = 'size'
    # Maximum page_size allowed for client
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number':self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })