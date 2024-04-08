from django.contrib import admin
from api.models import *
from django.contrib.admin import DateFieldListFilter
# Register your models here.
admin.site.site_header='后台管理'
admin.site.site_title='后台管理'
@admin.register(user)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email','last_login') # list
    search_fields = ('username',)
    ordering=['-date_joined']
    list_filter=[('date_joined',DateFieldListFilter)]
@admin.register(VipPoints)
class VipPointsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','points','source','create_time','is_active') # list
    search_fields = ('user__username',)
    ordering=['-create_time']
    list_filter=[('create_time',DateFieldListFilter),'is_active','user']
@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    list_display = ('user','active','content', 'create_time') # list
    search_fields = ('user__username',)
    ordering=['-create_time']
    list_filter=[('create_time',DateFieldListFilter),'active']

@admin.register(ClickItems)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('cid', 'user','item_id','create_time','last_update','is_active') # list
    search_fields = ('user','item_id')
    ordering=['-create_time','-last_update']
    list_filter=['user','is_active']
    
@admin.register(StarItems)
class StarAdmin(admin.ModelAdmin):
    list_display = ('sid', 'user','item_id','create_time','is_active') # list
    search_fields = ('user','item_id')
    ordering=['-create_time']
    list_filter=['user','is_active']
@admin.register(CommentItems)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('cid', 'user','content','item_id','create_time','is_active') # list
    search_fields = ('user','item_id')
    ordering=['-create_time']
    list_filter=['user','is_active']


