from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from datetime import date,datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils.mongo import MongoDB
from json import dumps,loads
from django.db.models import *
Mongo=MongoDB()

def user_directory_path(instance, filename):
    ext = filename.split('.').pop()
    filename = 'headerpic.'+ext
    return os.path.join(str(instance), filename)  # 系统路径分隔符差异，增强代码重用性
class GoodsName(models.Model):
    item_id=models.CharField(max_length=255,primary_key=True)
    # id=models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=255, verbose_name='饰品名称', db_index=True)
    icon_url=models.TextField(verbose_name='图片url')
    category=models.CharField(max_length=255, verbose_name='饰品分类')
    quality=models.CharField(max_length=255, verbose_name='饰品质量')
    rarity=models.CharField(max_length=255, verbose_name='饰品品质')
    type=models.CharField(max_length=255, verbose_name='饰品类型')
    exterior=models.CharField(max_length=255, verbose_name='饰品磨损')

    class Meta:
        verbose_name = '饰品名称'
        db_table = 'goods_name'  
        verbose_name_plural = verbose_name
    def to_dict(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'icon_url': self.icon_url,
            'category': self.category,
            'quality': self.quality,
            'rarity': self.rarity,
            'type': self.type,
            'exterior': self.exterior
        }
class CommentItems(models.Model):
    cid=models.BigAutoField(primary_key=True)
    user=models.ForeignKey('api.user', verbose_name="用户", on_delete=models.CASCADE)
    item_id=models.CharField(max_length=255, verbose_name='物品id', null=False)
    content=models.TextField(verbose_name='内容')
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    def to_dict(self):
        return {'id':self.cid,'item_id':self.item_id,'username':self.user.username,'content':self.content,'create_time':self.create_time}
    
    class Meta:
        verbose_name = '饰品评论列表'
        db_table = 'items_comments'  
        verbose_name_plural = verbose_name
class user(AbstractUser):

    name=models.CharField(max_length=10, verbose_name='姓名',null=True)
    steam_url=models.CharField(max_length=255, verbose_name='Steam主页链接',null=True)
    birth=models.DateField(verbose_name='生日',null=True)
    genderCode= models.IntegerField(default=1, verbose_name='性别id 男 1 女 0',null=True)
    genderTranslation= models.CharField(max_length=2, default='男', verbose_name='性别',null=True)
    phone = models.CharField(max_length=11, verbose_name='手机号', null=False)
    photo = models.ImageField('头像', upload_to=user_directory_path, blank=True, null=True,default='default/user.jpg')
    last_update = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')  
    vipTime=models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='vip到期时间')
    Inviter=models.EmailField(blank=True, null=True)
    @property
    def isvip(self):
         now=datetime.now().timestamp()
         if self.vipTime.timestamp()-now>0:
              return True
         return False
    @property
    def points(self):
        p=VipPoints.objects.filter(user_id=self.id, is_active=True).aggregate(total_points=Sum('points')).get('total_points')
        if not p:
            p=0
        return p
    @property
    def vip(self):
         if self.points<10 and self.isvip:
             return 1
         elif 30>self.points>=10:
              return 2
         elif 50>self.points>=30:
             return 3
         elif 70>self.points>=50:
             return 4
         elif 90>self.points>=70:
             return 5
         elif 150>self.points>=90:
             return 6
         elif 200>self.points>=150:
             return 7
         elif 500>self.points>=200:
             return 8
         elif self.points>=500:
             return 9
         return 0
    def to_dict(self):
        return {
            'username': self.name,
            # 'birth': self.birth.strftime('%Y-%m-%d') if self.birth else None,
            # 'genderCode': self.genderCode,
            # 'genderTranslation': self.genderTranslation,
            # 'phone': self.phone,
            'photo': self.photo.url if self.photo else None,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M:%S'),
            # 'points': self.points,
            # 'vipTime': self.vipTime.strftime('%Y-%m-%d %H:%M:%S') if self.vipTime else None,
            'isvip': self.isvip,
            'vip': self.vip
        }
    def __str__(self):
        return f'{self.username}'
    class Meta:
        verbose_name = '用户信息'
        db_table = 'user'
        verbose_name_plural = verbose_name
class VipPoints(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    points = models.FloatField(default=0)
    source=models.CharField(max_length=255, verbose_name='来源', null=False)
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    # 添加其他积分相关字段，如获取积分时间等
    class Meta:
        verbose_name = '用户VIP积分'
        db_table = 'vip_points'
        verbose_name_plural = verbose_name
class Announcement(models.Model):
    aid=models.BigAutoField(primary_key=True)
    title=models.TextField()
    content=models.TextField()
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    class Meta:
        verbose_name = '公告'
        db_table = 'announcement'
        verbose_name_plural = verbose_name
class Logs(models.Model):
    lid=models.BigAutoField(primary_key=True)
    user=models.ForeignKey(user, verbose_name="用户", on_delete=models.DO_NOTHING,null=True)
    active=models.TextField(verbose_name='行为')
    content=models.TextField(verbose_name='内容')
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    class Meta:
        verbose_name = '操作日志'
        db_table = 'logs'
        verbose_name_plural = verbose_name
        

class StarItems(models.Model):
    sid=models.BigAutoField(primary_key=True)
    user=models.ForeignKey('api.user', verbose_name="用户", on_delete=models.CASCADE)
    item_id=models.CharField(max_length=255, verbose_name='物品id', null=False)
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    class Meta:
        unique_together = ('item_id', 'user_id')
        verbose_name = '收藏列表'
        db_table = 'star_items'
        verbose_name_plural = verbose_name
        
class ClickItems(models.Model):
    cid=models.BigAutoField(primary_key=True)
    user=models.ForeignKey('api.user', verbose_name="用户", on_delete=models.CASCADE)
    item_id=models.CharField(max_length=255, verbose_name='物品id', null=False)
    count=models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    class Meta:
       
        unique_together = ('item_id', 'user_id')
        verbose_name = '浏览列表'
        db_table = 'click_items'
        verbose_name_plural = verbose_name


class CheckIn(models.Model):
    cid=models.BigAutoField(primary_key=True)
    user=models.ForeignKey('api.user', verbose_name="用户", on_delete=models.CASCADE)
    date = models.DateField(auto_now=False,auto_now_add=True, verbose_name='创建时间')
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False, verbose_name='最后修改时间')
    is_active=models.BooleanField(default=True, verbose_name='逻辑删除')
    class Meta:
        unique_together = ('date', 'user_id')
        verbose_name = '用户签到'
        db_table = 'user_checkin'
        verbose_name_plural = verbose_name
