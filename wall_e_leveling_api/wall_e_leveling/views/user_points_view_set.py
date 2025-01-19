from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.response import Response

from wall_e_leveling.views.pagination import StandardResultsSetPagination
from wall_e_models.customFields import pstdatetime
from wall_e_models.models import UserPoint, Level


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
            'points_needed_to_level_up', 'last_updated_date'
        ]


class UserPointViewSet(viewsets.ModelViewSet):
    serializer_class = UserPointSerializer
    queryset = UserPoint.objects.all().exclude(hidden=True).order_by('-points')
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def update(self, request, *args, **kwargs):
        return Response("not yet implemented")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        query = None
        timestamp = request.query_params.get('timestamp', None)
        include_null = request.query_params.get('include_null', None)
        include_null = include_null.lower() == 'true' if include_null else False
        if timestamp is not None and timestamp.isdigit():
            timestamp = pstdatetime.from_epoch(int(timestamp))
            query = Q(last_updated_date__gte=timestamp)
        if  include_null:
            if query:
                query = query | Q(last_updated_date__isnull=True)
            else:
                query = Q(last_updated_date__isnull=True)
        if query:
            queryset = queryset.filter(query)


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)