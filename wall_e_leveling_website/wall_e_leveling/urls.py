from django.urls import path, include
from rest_framework import routers

from wall_e_leveling.views.level_view_set import LevelViewSet
from wall_e_leveling.views.user_points_view_set import UserPointViewSet

router = routers.DefaultRouter()
router.register(r'user_points', UserPointViewSet, basename='user_points')
router.register(r'levels', LevelViewSet, basename='levels')

urlpatterns = [path(r'', include((router.urls, 'wall_e_leveling'), namespace="api"))]
