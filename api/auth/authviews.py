from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import *
from rest_framework.decorators import action
from api.auth.serializers import *
from ..utils.resp import *
from rest_framework.permissions import *
from rest_framework.throttling import *
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import viewsets
def authenticate(username=None, password=None, **kwargs):
    try:
        u = user.objects.get(phone=username)
    except:
        try:
            u = user.objects.get(username=username)
        except:
            try:
                u = user.objects.get(email=username)
            except:
                u = None
    if u and u.check_password(password):
        return u
def generate_tokens(user_object):
    access_token = AccessToken.for_user(user_object)
    refresh_token = RefreshToken.for_user(user_object)

    return {
        'access_token': str(access_token),
        'refresh_token': str(refresh_token),
    }
class InvitedList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            serializer=PageSerializer(data=request.GET)
            if serializer.is_valid():
                page=serializer.validated_data.get('page')
                pagesize=serializer.validated_data.get('pagesize')
                data=list(user.objects.filter(Inviter=request.user.email).order_by('-date_joined').values('email','date_joined')[(page-1)*pagesize:page*pagesize])

                return Resp.success(data=data,**{'page':page,'pagesize':pagesize})
            else:
                return Resp.failed(msg=serializer.errors)
        except Exception as e:
            return Resp.failed(msg=str(e))
class PointsList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            serializer=PageSerializerPoints(data=request.GET)
            if serializer.is_valid():
                page=serializer.validated_data.get('page')
                pagesize=serializer.validated_data.get('pagesize')
                type=serializer.validated_data.get('type')
                if type==0:
                    data=list(VipPoints.objects.filter(user=request.user).order_by('-create_time').values('source','points','create_time')[(page-1)*pagesize:page*pagesize])
                elif type==1:
                    data=list(VipPoints.objects.filter(user=request.user,points__gte=0).order_by('-create_time').values('source','points','create_time')[(page-1)*pagesize:page*pagesize])
                elif type==2:
                    data=list(VipPoints.objects.filter(user=request.user,points__lt=0).order_by('-create_time').values('source','points','create_time')[(page-1)*pagesize:page*pagesize])
                
                return Resp.success(data=data,**{'page':page,'pagesize':pagesize})
            else:
                return Resp.failed(msg=serializer.errors)
        except Exception as e:
            return Resp.failed(msg=str(e))
class Checkin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=CheckInSerializer(data=request.data)
        if serializer.is_valid():
            date=serializer.validated_data['date']
            isCheck=CheckIn.objects.filter(user=request.user,date=date).exists() 
            if not isCheck and date==datetime.datetime.now().date():
                date2=datetime.datetime.now()
                date2_add1=date+datetime.timedelta(days=1)
                CheckIn.objects.create(user=request.user,date=date)
                VipPoints.objects.create(user=request.user,source='签到奖励',points=0.5)
                user.objects.filter(id=request.user.id).update(vipTime=date2_add1)
                return Resp.success(msg='签到成功')
            elif isCheck and date==datetime.datetime.now().date():
                return Resp.failed(msg='今日已签到')
            elif isCheck and date!=datetime.datetime.now().date():
                return Resp.failed(msg='已签到')
            elif not isCheck and date!=datetime.datetime.now().date():
                return Resp.failed(msg='时间未到或签到已过期')
            else:
                return Resp.failed()
        else:
            return Resp.failed(msg=serializer.errors)


class CheckinList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=CheckInListSerializer(data=request.data)
        if serializer.is_valid():
            year=serializer.validated_data['year']
            month=serializer.validated_data['month']
            
            data=list(CheckIn.objects.filter(user=request.user,date__year=year,date__month=month).annotate(info=Value('已签到')).values('date','info'))
            return Resp.success(data=data)
            
        else:
            return Resp.failed(msg=serializer.errors)
class UserInfoView(viewsets.ViewSet):
    """
    返回用户基本信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset =user.objects.all().filter(is_active=True)
    def isvip(self,data):
         now=datetime.datetime.now().timestamp()
         try:
            date=datetime.datetime.strptime(data['vipTime'], '%Y-%m-%dT%H:%M:%S.%f')
         except:
             date=datetime.datetime.strptime(data['vipTime'], '%Y-%m-%dT%H:%M:%S')
         if date.timestamp()-now>0:
              return True
         return False
    def points(self,data):
        p=VipPoints.objects.filter(user=self.request.user, is_active=True).aggregate(total_points=Sum('points')).get('total_points')
        if not p:
            p=0
        return p
    def vip(self,data):
         if data['points']<10 and data['isvip']:
             return 1
         elif 30>data['points']>=10:
              return 2
         elif 50>data['points']>=30:
             return 3
         elif 70>data['points']>=50:
             return 4
         elif 90>data['points']>=70:
             return 5
         elif 150>data['points']>=90:
             return 6
         elif 200>data['points']>=150:
             return 7
         elif 500>data['points']>=200:
             return 8
         elif data['points']>=500:
             return 9
         return 0
    def stars(self,data):
        s=StarItems.objects.filter(user=self.request.user, is_active=True).aggregate(total_stars=Count('item_id')).get('total_stars')
        if not s:
            s=0
        return s
    def historys(self,data):
        s=ClickItems.objects.filter(user=self.request.user, is_active=True).aggregate(total_historys=Count('item_id')).get('total_historys')
        if not s:
            s=0
        return s
    def comments(self,data):
        c=CommentItems.objects.filter(user=self.request.user, is_active=True).aggregate(total_comments=Count('item_id')).get('total_comments')
        if not c:
            c=0
        return c
    def checkin(self,data):
        c=CheckIn.objects.filter(user=self.request.user, date=datetime.datetime.now().date()).exists()
        return c
    @action(detail=False, methods=['GET'])
    def getinfo(self, request, *args, **kwargs):
        
        Serializer = UserInfoSerializer(request.user)
        data=Serializer.data.copy()
        data['points']=self.points(data)
        data['stars']=self.stars(data)
        data['historys']=self.historys(data)
        data['notifications']=0
        data['comments']=self.comments(data)
        data['isvip']=self.isvip(data)
        data['checkin']=self.checkin(data)
        data['vip']=self.vip(data)
        
        return Response({'code': 200, 'msg': "成功",'data':data})
    @action(detail=False, methods=['POST'])
    def uploadPhoto(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=PhotoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
    @action(detail=False, methods=['POST'])
    def updateName(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=NameSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
                data['data']=serializer.validated_data
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
    @action(detail=False, methods=['POST'])
    def updateSteamUrl(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=SteamUrlSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
                data['data']=serializer.validated_data
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
    @action(detail=False, methods=['POST'])
    def updateBirth(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=BirthSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
    @action(detail=False, methods=['POST'])
    def updatePhone(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=PhoneSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
    @action(detail=False, methods=['POST'])
    def updateSex(self,request):
        data={
            'code':'200',
            'data':None,
            'msg':'ok',
        }
        try:
            serializer=SexSerializer(data=request.data)
            if serializer.is_valid():
                serializer.update(request.user,serializer.validated_data)
            else:
                data['code']='501'
                data['msg']=serializer.errors
        except Exception as e:
            data['code']='500'
            data['msg']=str(e)
        return Response(data)
# 注册账号
class SignupView(APIView):
    # 局部认证类：无需认证即可访问此视图，优先级高于全局认证类
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        
        Serializer = UserRegisterSerializer(data=request.data)
        if Serializer.is_valid():
            Serializer.save()
            Inviter=Serializer.validated_data.get('Inviter')
            if Inviter:
                u=user.objects.get(email=Inviter)
                VipPoints.objects.create(user=u,source='邀请用户',points=10)
                if u.Inviter:
                    u2=user.objects.get(email=u.Inviter)
                    VipPoints.objects.create(user=u2,source='二级邀请用户',points=3)
                    if u2.Inviter:
                        u3=user.objects.get(email=u2.Inviter)
                        VipPoints.objects.create(user=u3,source='三级邀请用户',points=1)
            VipPoints.objects.create(user=request.user,points=10,source='注册奖励')
            return Response({'code': 200, 'msg': "注册成功"})
            
        else:
            errors={
                'non_field_errors':501,
                'name':502,
                'email':503,
                'password':504,
                'checkpassword':505,
                'code':506
            }
            for i in Serializer.errors.keys():
                return Response({'code': errors.get(i,507), 'error': Serializer.errors.get(i)[0]})

class LoginView(APIView):
    # 局部认证类：无需认证即可访问此视图，优先级高于全局认证类
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        Serializer = UserLoginSerializer(data=request.data)
        code=request.data.get('code')
        rel_code=request.COOKIES.get('captcha')

        if not rel_code or not code or not check_password(code.lower(),rel_code):
            resp=Response({'code': 501, 'error': "验证码错误!"})
            resp.delete_cookie('captcha')
            return resp
        if Serializer.is_valid():
            
            account=Serializer.data['account']
            password=Serializer.data['pwd']
            user_object=authenticate(username=account,password=password)
            
            # 若账号不在账号表中，即未搜索到user_post对应的username的对象
            if not user_object:
                # 返回字符串： return Response("用户不存在")
                resp=Response({'code': 502, 'error': "用户名或密码不正确"})
                resp.delete_cookie('captcha')
                return resp
            elif not user_object.is_active:
                resp=Response({'code': 503, 'error': "账号禁用"})
                resp.delete_cookie('captcha')
                return resp
            Serializer.update(user_object,Serializer.validated_data)
            resp=Response({'code': 200, 'tokens': generate_tokens(user_object)})
            resp.delete_cookie('captcha')
            return resp

        else:
            errors={
                'non_field_errors':504,
                'pwd':505,
                'account':506
            }
            for i in Serializer.errors.keys():
                resp=Response({'code': errors.get(i,507), 'error': Serializer.errors.get(i)[0]})
                resp.delete_cookie('captcha')
                return resp

    



class ForegetPSWView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        Serializer = UserForegetSerializer(data=request.data)
        if Serializer.is_valid():
            u=user.objects.get(email=Serializer.validated_data.get('email'))
            Serializer.update(u,Serializer.validated_data)
            return Response({'code': 200,'msg': '修改成功！'})         
        else:
            errors={
                'non_field_errors':501,
                'email':502,
                'password':503,
                'checkpassword':504,
                'code':505,
            }
            for i in Serializer.errors.keys():
                return Response({'code': errors.get(i,506), 'error': Serializer.errors.get(i)[0]})
