"""
URL Configuration for leads app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, StageViewSet, ConfigViewSet

router = DefaultRouter()
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"stages", StageViewSet, basename="stage")
router.register(r"config", ConfigViewSet, basename="config")

urlpatterns = [
    path("", include(router.urls)),
]
