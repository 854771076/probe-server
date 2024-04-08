from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import *
from django.conf import settings
from rest_framework.decorators import action
from api.feedback.serializers import *
from rest_framework.permissions import *
from rest_framework.throttling import *
from ..utils.resp import *
from ..utils.email import *
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import viewsets
class SendFeedBackView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer=QuestionSerializer(data=request.data)
        try:
            if serializer.is_valid():
                send_Email(serializer.validated_data.get('title'),[serializer.validated_data.get('question')],[settings.FEEDBACK_EMAIL],request.user.email)
                return Resp.success()
            else:
                return Resp.failed(msg=serializer.errors)
        except Exception as e:
            Resp.failed(msg=str(e))
