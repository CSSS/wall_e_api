from rest_framework import serializers, viewsets
from rest_framework.response import Response

from wall_e_leveling.views.pagination import StandardResultsSetPagination
from wall_e_models.models import Level


class LevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Level
        fields = ['id', 'number', 'total_points_required', 'role_name']


class LevelViewSet(viewsets.ModelViewSet):
    serializer_class = LevelSerializer
    queryset = Level.objects.all().order_by('-number')
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")