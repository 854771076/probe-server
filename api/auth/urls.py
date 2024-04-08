from django.contrib import admin
from django.urls import path, include
from api.auth.authviews import *
from rest_framework.routers import DefaultRouter
from ..middlewares import *

router = DefaultRouter()
router.register(r"userinfo", UserInfoView)


if  settings.DEBUG:
    urlpatterns = [
        path("login/", LoginView.as_view()),
        path("signup/", SignupView.as_view()),
        path("foreget/", ForegetPSWView.as_view()),
        path("checkin/", NotSpiderMiddlewareDefualt(Checkin.as_view())),
        path("checkin-list/", CheckinList.as_view()),
        path("invited-list/", InvitedList.as_view()),
        path("points-list/", PointsList.as_view()),
    ]
else:
    urlpatterns = [
        path("login/", LoginView.as_view()),
        path("signup/", SignupView.as_view()),
        path("foreget/", ForegetPSWView.as_view()),
        path("checkin/", NotSpiderMiddlewareDefualt(Checkin.as_view())),
        path("checkin-list/", NotSpiderMiddlewareDefualt(CheckinList.as_view())),
        path("invited-list/", NotSpiderMiddlewareDefualt(InvitedList.as_view())),
        path("points-list/", NotSpiderMiddlewareDefualt(PointsList.as_view())),
    ]
urlpatterns += router.urls
