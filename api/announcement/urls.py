from api.announcement.views import *
from django.urls import path,include
urlpatterns = [

    path('getannouncementlist',GetAllAnnouncementList.as_view()),
]