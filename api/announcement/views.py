from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Announcement
from rest_framework.permissions import *
from rest_framework.throttling import *
from rest_framework_simplejwt.authentication import JWTAuthentication
class GetAllAnnouncementList(APIView):
	authentication_classes = [JWTAuthentication]
	permission_classes = [AllowAny]
	def get(self, request, *args, **kwargs):
		data={
			'code':'200',
			'data':list(Announcement.objects.filter(is_active=True).order_by('-create_time').order_by('-last_update').values()),
			'msg':'OK'
		}
		return Response(data)
		