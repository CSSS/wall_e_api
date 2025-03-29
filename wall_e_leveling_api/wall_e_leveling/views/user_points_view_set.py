import django_filters
from django.db.models import Q
from django.utils.safestring import mark_safe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, generics
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

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
class UserFilterSet(django_filters.FilterSet):
    class Meta:
        model = UserPoint
        fields = {
            'last_updated_date' : ['gte', 'isnull']
        }

def create_last_updated_date__isnull_query(include_null, query):
    if query:
        if include_null:
            return query | Q(last_updated_date__isnull=include_null)
    else:
        if include_null:
            return Q(last_updated_date__isnull=include_null)
    return None


class UserPointViewSet(ViewSetMixin, generics.ListAPIView):
    queryset = UserPoint.objects.all().exclude(hidden=True).order_by('-points')
    serializer_class = UserPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends =  [DjangoFilterBackend]
    filterset_class = UserFilterSet

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        timestamp = request.query_params.get('last_updated_date__gte', '')
        if (timestamp != '' and timestamp.isdigit()):
            timestamp = pstdatetime.from_epoch(int(timestamp))
        else:
            timestamp = None if timestamp == 'None' else pstdatetime.from_epoch(0)
        query = Q(last_updated_date__gte=timestamp) if timestamp else None


        include_null = request.query_params.get('last_updated_date__isnull', '')
        if include_null == '':
            include_null = True
        elif include_null == 'unknown':
            include_null = False
        else:
            include_null = True if include_null.lower() == 'true' else False
        isnull_query = create_last_updated_date__isnull_query(include_null, query)
        if isnull_query:
            query = isnull_query
        if query:
            queryset = queryset.filter(query)


        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(mark_safe(serializer.data))