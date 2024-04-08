from django.contrib import admin
from django.urls import path,include
from api.feedback.feedbackviews import *

urlpatterns = [
	path('send', SendFeedBackView.as_view()),
]