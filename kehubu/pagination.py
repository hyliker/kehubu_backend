from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict
import urllib.parse as urlparse


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    def get_query(self, link):
        tokens = urlparse.urlparse(link)
        query_params = urlparse.parse_qs(tokens.query)
        if not query_params:
            return None

        params = dict()
        for k, v in query_params.items():
            params[k] = v[0]
        return params

    def get_next_query(self):
        next_link = self.get_next_link()
        return self.get_query(next_link)

    def get_previous_query(self):
        link = self.get_previous_link()
        return self.get_query(link)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('next_query', self.get_next_query()),
            ('previous', self.get_previous_link()),
            ('previous_query', self.get_previous_query()),
            ('results', data)
        ]))
