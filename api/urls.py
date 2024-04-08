from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
urlpatterns = [
    path('auth/', include('api.auth.urls')),
    path('code/', include('api.code.urls')),
    path('announcement/', include('api.announcement.urls')),
    path('goods/', include('api.goods.urls')),
    path('feedback/', include('api.feedback.urls')),
    path('token/refresh/', TokenRefreshView.as_view()),
]
