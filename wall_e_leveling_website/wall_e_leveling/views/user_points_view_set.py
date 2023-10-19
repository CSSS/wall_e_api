from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from wall_e_models.models import UserPoint


class UserPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPoint
        fields = '__all__'

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        next_link = self.get_next_link().replace(":443", "")
        previous_link = self.get_previous_link().replace(":443", "")
        return Response({
            'links': {
               'next': next_link,
               'previous': previous_link
            },
            'count': self.page.paginator.count,
            'total_number_of_pages': self.page.paginator.num_pages,
            'results': data
        })


class UserPointViewSet(viewsets.ModelViewSet):
    serializer_class = UserPointSerializer
    queryset = UserPoint.objects.all()
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")