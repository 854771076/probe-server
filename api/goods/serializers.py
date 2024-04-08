from rest_framework import serializers
from api.models import *
class GoodSerializer(serializers.Serializer):
    item_id=serializers.CharField(min_length=0,max_length=100,required=True)
    days=serializers.IntegerField(max_value=365,min_value=1,default=7)
class CommentsSerializer(serializers.ModelSerializer):
    user=serializers.DjangoModelField(user)
    item_id=serializers.ReadOnlyField()
    is_mine=serializers.ReadOnlyField()
    class Meta:
        model = CommentItems
        exclude =['is_active']
        extra_kwargs = {
            'user': {'required': False}
        }
    def create(self, validated_data):
        # 在创建对象时允许设置 item_id 字段
        data=validated_data.copy()
        data['item_id']=self.initial_data.get('item_id')
        instance = CommentItems.objects.create(**data)
        return instance
class StarsSerializer(serializers.ModelSerializer):
    user=serializers.DjangoModelField(user)
    
    class Meta:
        model = StarItems
        exclude =['is_active']
        extra_kwargs = {
            'user': {'required': False}
        }

    def validate(self, attrs):

        return attrs
class ClicksSerializer(serializers.ModelSerializer):
    user=serializers.DjangoModelField(user)
    class Meta:
        model = ClickItems
        exclude =['is_active']
        extra_kwargs = {
            'user': {'required': False}
        }

class PageSerializer(serializers.Serializer):
    
    pagesize=serializers.IntegerField(max_value=20,min_value=1,default=20)
    page=serializers.IntegerField(min_value=1,default=1,max_value=50)
    name=serializers.CharField(min_length=0,max_length=100,default='')
    sort=serializers.IntegerField(default=0)
    exterior=serializers.CharField(min_length=0,max_length=100,default=None)
    quality=serializers.CharField(min_length=0,max_length=100,default=None)
    type=serializers.CharField(min_length=0,max_length=100,default=None)
    rarity=serializers.CharField(min_length=0,max_length=100,default=None)
    price_gte=serializers.IntegerField(default=None)
    price_lte=serializers.IntegerField(default=None)

