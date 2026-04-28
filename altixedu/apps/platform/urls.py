from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AIRiskAlertViewSet,
    AnnouncementViewSet,
    BrandingAdminAPIView,
    BrandingPublicAPIView,
    PlatformHealthAPIView,
    PlatformOverviewAPIView,
    SchoolRegistrationAPIView,
    SubdomainCheckAPIView,
)

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet, basename='platform-announcements')
router.register(r'ai-risk-alerts', AIRiskAlertViewSet, basename='platform-ai-risk-alerts')

app_name = 'platform'

urlpatterns = [
    path('', include(router.urls)),
    path('overview/', PlatformOverviewAPIView.as_view(), name='platform-overview'),
    path('health/', PlatformHealthAPIView.as_view(), name='platform-health'),
    path('branding/', BrandingPublicAPIView.as_view(), name='branding-public'),
    path('branding-admin/', BrandingAdminAPIView.as_view(), name='branding-admin'),
    path('check-subdomain/', SubdomainCheckAPIView.as_view(), name='check-subdomain'),
    path('register-school/', SchoolRegistrationAPIView.as_view(), name='register-school'),
]
