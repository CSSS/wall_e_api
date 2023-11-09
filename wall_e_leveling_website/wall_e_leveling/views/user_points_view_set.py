from rest_framework import serializers, viewsets
from rest_framework.response import Response
from wall_e_models.models import UserPoint, Level

from wall_e_leveling.views.pagination import StandardResultsSetPagination


class UserPointSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField('get_name')

    avatar = serializers.SerializerMethodField('get_avatar')

    points_needed_to_level_up = serializers.SerializerMethodField('get_points_needed_to_level_up')

    def get_name(self, user):
        if user.nickname is not None:
            return user.nickname
        return user.name

    def get_avatar(self, user):
        return user.leveling_message_avatar_url

    def get_points_needed_to_level_up(self, user):
        current_level = Level.objects.all().filter(
            total_points_required__lte=user.points
        ).order_by('-total_points_required').first()
        return current_level.xp_needed_to_level_up_to_next_level

    class Meta:
        model = UserPoint
        fields = [
            'name', 'avatar', 'points', 'level_number', 'message_count', 'level_up_specific_points',
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