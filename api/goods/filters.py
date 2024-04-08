from api.models import *
from django_filters import rest_framework as filters
class CommentsFilter(filters.FilterSet):
    item_id = filters.CharFilter(lookup_expr='exact')
    email= filters.CharFilter(lookup_expr='exact',field_name="user__email")
    class Meta:
        model = CommentItems
        fields = '__all__'
        
class StarsFilter(filters.FilterSet):

    class Meta:
        model = StarItems
        fields = '__all__'
class ClickFilter(filters.FilterSet):

    class Meta:
        model = ClickItems
        fields = '__all__'