from django.urls import path,include
from api.goods.goodsviews import *
from rest_framework.routers import DefaultRouter
from ..middlewares import *
router = DefaultRouter()
router.register(r'comments', CommentsViewSet)
router.register(r'stars', StarsViewSet)
router.register(r'history', ClicksViewSet)
if  settings.DEBUG:
    urlpatterns = [
        path('detail/<str:item_id>', GoodsDetail.as_view()),
        path('list/<str:col>', GoodsList.as_view()),
        path('list_download/<str:col>', GoodsListDownload.as_view()),
        path('list_leaks/<str:col>', GoodsLeaksList.as_view()),
        path('associated_words', AssociatedWords.as_view()),
        path('goods_history_price', Goods_price_List.as_view()),
        path('my_goods',My_Goods_List.as_view()),
    ]
else:
    urlpatterns = [
        path('detail/<str:item_id>', NotSpiderMiddleware(GoodsDetail.as_view())),
        path('list/<str:col>', NotSpiderMiddleware2(GoodsList.as_view())),
        path('list_download/<str:col>', NotSpiderMiddleware2(GoodsListDownload.as_view())),
        path('list_leaks/<str:col>',NotSpiderMiddleware2(GoodsLeaksList.as_view())),
        path('associated_words', AssociatedWords.as_view()),
        path('goods_history_price', NotSpiderMiddlewareDefualt(Goods_price_List.as_view())),
        path('my_goods',My_Goods_List.as_view()),
    ]
urlpatterns += router.urls