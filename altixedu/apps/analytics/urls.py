from django.urls import path
from .views import advanced_analytics_dashboard

urlpatterns = [
    path('advanced-analytics/', advanced_analytics_dashboard, name='advanced-analytics'),
]
