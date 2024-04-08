from rest_framework import serializers
from api.models import user
import datetime
from django.utils.translation import ugettext_lazy as _
from api.utils.redis import getRedisConnection
from django.contrib.auth.hashers import make_password,check_password
class UserRegisterSerializer(serializers.ModelSerializer):
    username=serializers.CharField(required=False,min_length=4,max_length=100)
    password=serializers.CharField(required=True,min_length=8,max_length=16)
    checkpassword=serializers.CharField(required=True,min_length=8,max_length=16)
    email = serializers.EmailField(required=True,max_length=50)
    phone=serializers.CharField(required=True,min_length=8,max_length=11)
    code=serializers.CharField(required=True,min_length=6,max_length=6)
    Inviter=serializers.EmailField(required=False,max_length=50)
    class Meta:
        model=user
        fields=['username','password','checkpassword','email','phone','code','name','Inviter']
    def create(self, validated_data):
        validated_data.pop('code')
        validated_data.pop('checkpassword')
        validated_data['username']='JF'+str(100000+user.objects.all().count())
        validated_data['name']='JF'+str(100000+user.objects.all().count())
        u = user.objects.create(**validated_data)
        return u
    def validate_email(self,data):
        try:
            user.objects.get(email=data)
        except user.DoesNotExist:
            return data
        raise serializers.ValidationError(_("邮箱已注册"))
    def validate_Inviter(self,data):
        try:
            user.objects.get(email=data)
            
            return data
        except user.DoesNotExist:
            raise serializers.ValidationError(_("邀请者未注册"))
    def validate_phone(self,data):
        try:
            user.objects.get(phone=data)
        except user.DoesNotExist:
            return data
        raise serializers.ValidationError(_("手机号已注册"))
    def validate_code(self,data):
        
        code=getRedisConnection().get(self.initial_data['email'])
        if not code:
            raise serializers.ValidationError(_("请发送验证码"))
        if data!=code:
            raise serializers.ValidationError(_("验证码错误"))
        return data
    def validate(self,data):
        
        if 'password' in data and 'checkpassword' in data:
            if data['password'] != data['checkpassword']:
                raise serializers.ValidationError(_("两次密码不一致"))
        data['password']=make_password(data['password'])
        return data           
class UserLoginSerializer(serializers.ModelSerializer):
    account=serializers.CharField(required=True,min_length=4,max_length=100)
    pwd=serializers.CharField(required=True,min_length=8,max_length=16)

    class Meta:
        model=user
        fields=['account','pwd','last_login']
   
    def validate(self,data):
        try:
            a=user.objects.get(phone=data['account'])
            data['account']=a
            # data['type']='phone'
        except user.DoesNotExist:
            try:
                a=user.objects.get(email=data['account'])
                data['account']=a
                # data['type']='email'
            except user.DoesNotExist:
                try:
                    a=user.objects.get(username=data['account'])
                    data['account']=a
                    # data['type']='username'
                except user.DoesNotExist:
                    raise serializers.ValidationError(_("账号未注册！"))
        data['last_login']=datetime.datetime.now()
        return data
class PhotoSerializer(serializers.ModelSerializer):
    
    file=serializers.FileField(required=True, source='photo')
    class Meta:
        model=user
        fields = ['file']
        extra_kwargs = {
            'file': {'required': True}
        }
class NameSerializer(serializers.ModelSerializer):
    name=serializers.CharField(required=True,min_length=1,max_length=100)
    class Meta:
        model=user
        fields = ['name']
class SteamUrlSerializer(serializers.ModelSerializer):
    steam_url=serializers.CharField(required=True,min_length=1,max_length=255)
    class Meta:
        model=user
        fields = ['steam_url']
class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=user
        fields = ['phone']
    def validate_phone(self,data):
        try:
            user.objects.get(phone=data)
        except user.DoesNotExist:
            return data
        raise serializers.ValidationError(_("手机号已注册"))
class SexSerializer(serializers.ModelSerializer):
    class Meta:
        model=user
        fields = ['genderCode','genderTranslation'] 
    def validate_genderCode(self,data):
        if  data in (0,1):
            return data
        else:
            raise serializers.ValidationError(_("性别不正确"))
    def validate_genderTranslation(self,data):
        if  data in ("男","女"):
            return data
        else:
            raise serializers.ValidationError(_("性别不正确"))
class BirthSerializer(serializers.ModelSerializer):
    class Meta:
        model=user
        fields = ['birth'] 
class PageSerializer(serializers.Serializer):
    
    pagesize=serializers.IntegerField(max_value=20,min_value=1,default=20)
    page=serializers.IntegerField(min_value=1,default=1,max_value=50)
class PageSerializerPoints(serializers.Serializer):
    
    pagesize=serializers.IntegerField(max_value=20,min_value=1,default=20)
    page=serializers.IntegerField(min_value=1,default=1,max_value=50)
    type=serializers.IntegerField(min_value=0,default=0,max_value=3)
class CheckInSerializer(serializers.Serializer):
    
    date=serializers.DateField(required=True)  
class CheckInListSerializer(serializers.Serializer):
    year=serializers.IntegerField(required=True)
    month=serializers.IntegerField(required=True)
class UserForegetSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True,max_length=50)
    password=serializers.CharField(required=True,min_length=8,max_length=16)
    checkpassword=serializers.CharField(required=True,min_length=8,max_length=16)
    code=serializers.CharField(required=True,min_length=6,max_length=6)

    class Meta:
        model=user
        fields=['email','password','checkpassword','code']

    def validate_code(self,data):
            
        code=getRedisConnection().get(self.initial_data['email'])
        if not code:
            raise serializers.ValidationError(_("请发送验证码"))
        if data!=code:
            raise serializers.ValidationError(_("验证码错误"))
        return data
    def validate_email(self,data):
        try:
            user.objects.get(email=data)
            return data
        except user.DoesNotExist:
            raise serializers.ValidationError(_("邮箱未注册！"))
    def validate(self,data):
        U=user.objects.get(email=data['email'])
        if data['password'] != data['checkpassword']:
            raise serializers.ValidationError(_("两次密码不一致！"))
        if check_password(data['password'],U.password):
            raise serializers.ValidationError(_("新旧密码不可相同！"))
        
        data['password']=make_password(data['password'])
        return data    
class UserInfoSerializer(serializers.ModelSerializer):


    class Meta:
        model = user
        exclude = ['password','groups','user_permissions','first_name','last_name','id']