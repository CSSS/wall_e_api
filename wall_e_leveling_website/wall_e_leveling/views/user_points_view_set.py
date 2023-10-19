from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from wall_e_models.models import UserPoint


class UserPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPoint
        fields = '__all__'


class UserPointViewSet(viewsets.ModelViewSet):
    serializer_class = UserPointSerializer

    def get_objects(self):
        return UserPoint.objects.get(id=int(self.kwargs['pk']))

    def list(self, request, *args, **kwargs):
        return Paginator(
            UserPoint.objects.all(), 25
        ).page(0).object_list