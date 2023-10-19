from rest_framework import serializers, viewsets
from rest_framework.response import Response
from wall_e_models.models import UserPoint, Level

from wall_e_leveling.views.pagination import StandardResultsSetPagination


class UserPointSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField("get_username")

    points_needed_to_level_up = serializers.SerializerMethodField('get_points_needed_to_level_up')

    def get_username(self, user):
        return user.username

    def get_points_needed_to_level_up(self, user):
        current_level = Level.objects.all().filter(
            total_points_required__lte=user.points
        ).order_by('-total_points_required').first()
        return current_level.xp_needed_to_level_up_to_next_level

    class Meta:
        model = UserPoint
        fields = [
            'username', 'points', 'level_number', 'message_count', 'level_up_specific_points',
            'points_needed_to_level_up'
        ]


class UserPointViewSet(viewsets.ModelViewSet):
    serializer_class = UserPointSerializer
    queryset = UserPoint.objects.all().exclude(hidden=True)
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")