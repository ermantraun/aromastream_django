from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView)
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('login/', TokenObtainSlidingView.as_view(), name='login'),
    path('signup/', views.UserCreateView.as_view(), name='signup'),
    path('user/', views.UserGetView.as_view(), name='user'),
    path('user/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('password_reset/', views.UserPasswordUpdateView.as_view(), name='password_reset'),
    path('password_reset/confirm/', views.UserPasswordUpdateConfirmView.as_view(), name='password_reset_confirm'),
    path('timestamps/', views.TimeStampCreateView.as_view(), name='timestamp_create'),
    path('timestamps/<int:video_id>/', views.TimeStampListView.as_view(), name='timestamp_list'),
    path('videos/', views.VideoListView.as_view(), name='videos'),
    path('videos/<int:video_id>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('videos/popular/', views.PopularVideoListView.as_view(), name='popular_videos'),
    path('videos/search/', views.SearchVideoListView.as_view(), name='search_video'),
    path('arduino/trigger', views.TriggerListView.as_view(), name='trigger'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]