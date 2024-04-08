from rest_framework import viewsets
from .serializers import *
from .filters import *
from api.models import *
from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters
from rest_framework.decorators import action
import csv
from django.http import HttpResponse
from ..utils.encrypt import *
from ..utils.resp import *
from django.db.models import *
from django.db.models.functions import *
from rest_framework import permissions
from rest_framework.response import Response
from json import dumps
from ..middlewares import *
from rest_framework.throttling import *
from django.utils.decorators import method_decorator
from django.db.models import F, ExpressionWrapper, fields
from django.views.decorators.cache import cache_page
import re,requests


def utf8_encode(data):
    if isinstance(data, dict):
        return {k: utf8_encode(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [utf8_encode(item) for item in data]
    elif isinstance(data, str):
        return data.encode("utf-8")
    else:
        return data


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 在这里编写权限逻辑，返回 True 表示有权限，返回 False 表示没有权限
        if request.method == "GET":
            return True
        elif (
            request.method in ("POST", "PUT", "DELETE")
            and request.user
            and request.user.is_authenticated
        ):
            return True
        else:

            return False

    def has_object_permission(self, request, view, obj):
        # 在这里编写对象级别的权限逻辑，返回 True 表示有权限，返回 False 表示没有权限
        if request.method == "GET":
            return True
        else:
            if hasattr(obj, "user"):
                # 验证请求的用户是否与对象的用户匹配
                return obj.user == request.user
            else:
                return False


class CustomPermission2(permissions.BasePermission):
    def has_permission(self, request, view):
        # 在这里编写权限逻辑，返回 True 表示有权限，返回 False 表示没有权限

        if (
            request.method in ("GET", "POST", "DELETE")
            and request.user
            and request.user.is_authenticated
        ):
            return True
        else:

            return False

    def has_object_permission(self, request, view, obj):
        # 在这里编写对象级别的权限逻辑，返回 True 表示有权限，返回 False 表示没有权限

        if hasattr(obj, "user"):
            # 验证请求的用户是否与对象的用户匹配
            return obj.user == request.user and request.user.is_authenticated
        else:
            return False


class VIPPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # 在这里编写权限逻辑，返回 True 表示有权限，返回 False 表示没有权限

        if (
            request.method in ("GET", "POST", "DELETE")
            and request.user.is_authenticated
        ):
            return True
        else:

            return False

    def has_object_permission(self, request, view, obj):
        # 在这里编写对象级别的权限逻辑，返回 True 表示有权限，返回 False 表示没有权限

        if hasattr(obj, "user"):
            # 验证请求的用户是否与对象的用户匹配
            return obj.user == request.user and request.user.is_authenticated
        else:
            return False


class AssociatedThrottle(UserRateThrottle):
    rate = "200/m"


class AssociatedWords(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [AssociatedThrottle]

    def get(self, request):
        keywords = request.GET.get("keywords")
        if keywords:
            data = GoodsName.objects.filter(name__icontains=keywords)[:10].values(
                "name"
            )
            for i in data:
                match = re.findall(f".*({keywords}).*", i.get("name"), re.IGNORECASE)[0]
                match2 = '<span style="color:#ffb700">' + match + "</span>"
                i["value"] = i["name"]
                i["name"] = i["name"].replace(match, match2)

            return Resp.success(data=data)
        else:
            return Resp.success(data=[])


class GoodsListDownload(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [VIPPermission]

    def get(self, request, col=None):
        if request.user.isvip and request.user.vip >= 8:
            VipPoints.objects.create(user=request.user, points=-1, source="下载资源")
            serializer = PageSerializer(data=request.GET)
            if serializer.is_valid():
                datas = Mongo.get_pages_all(col, **serializer.validated_data)
                date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = (
                    f'attachment; filename="{col}_{date}.csv"'
                )
                response.headers["Filename"] = f"{col}_{date}.csv"
                # 创建CSV写入器
                writer = csv.writer(response)

                # 写入CSV标题行
                header = [
                    field
                    for field in list(Mongo.collections[col].keys())
                    if field not in ["today"]
                ]
                writer.writerow(header)  # 添加需要导出的字段名称
                res = []
                # 写入查询结果到CSV文件
                for data in datas:
                    d = []
                    for field in header:
                        if field in header:
                            d.append(data.get(field, ""))
                    res.append(d)
                writer.writerows(res)

                return response
            else:
                return Resp.failed(msg=serializer.errors)
        else:
            return Resp.failed(msg="vip到期,或等级不足vip8")
class My_Goods_List(APIView):
    '''
    我的饰品
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            if request.user.isvip and request.user.vip >= 2:
                headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'Connection': 'keep-alive',
                    'Referer': 'https://steamcommunity.com/search/users/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
                url=request.user.steam_url
                if url.find('steamcommunity.com/id')!=-1:
                    r=requests.get(url)
                    text=re.sub('\s','',r.text)
                    steamid=re.findall('"steamid":"(.*?)",',text)[0]
                elif url.find('steamcommunity.com/profiles')!=-1:
                    steamid=url.split('/')[-1].strip('/')
                else:
                    return Resp.failed(msg='链接有误')
                r=requests.get(f'https://steamcommunity.com/inventory/{steamid}/730/2?l=schinese&count=5000',headers=headers)
                res=[]
                total=r.json().get('total_inventory_count',0)
                for i in r.json().get('descriptions',[]):
                    md5 = hashlib.md5()
                    md5.update(i.get('market_hash_name').encode('utf-8'))
                    for j in i.get('tags',[]):
                        i[j['category'].lower()]=j['localized_tag_name']
                    i['icon_url']='https://steamcommunity-a.akamaihd.net/economy/image/'+i['icon_url']
                    i['item_id']=md5.hexdigest()
                    res.append(i)
                return Resp.success(data=res,**{'total':total,"page": 1,"pagesize": 5000})
            else:
                return Resp.failed(msg="vip到期,或等级不足vip2,请签到")
        except Exception as e:
            return Resp.failed(msg=str(e))
class Goods_price_List(APIView):
    '''
    饰品历史价格
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomPermission]
    star_queryset = StarItems.objects.filter(is_active=1)
    def get(self, request):
        serializer = GoodSerializer(data=request.GET)
        if serializer.is_valid():
            res={}
            cols = ["steam_csgo","buff_csgo", "uuyp_csgo", "c5_csgo", "igxe_csgo"]
            for col in cols:
                res[col]=Mongo.get_item_archive(col,serializer.validated_data.get('item_id'),serializer.validated_data.get('days'))
            if not settings.DEBUG:
                data = dumps(
                    {
                        "data": res,
                        "code": "200",
                        "msg": "ok",
                    },
                    ensure_ascii=False,
                    default=datetime_serialization_handler,
                )
            else:
                data = aes_encrypt(
                    dumps(
                        {
                            "data": res,
                            "code": "200",
                            "msg": "ok",
                        },
                        ensure_ascii=True,
                        default=datetime_serialization_handler,
                    )
                )
            resp = HttpResponse(data)

            return resp
        else:
            return Resp.failed(msg=serializer.errors)

class GoodsList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomPermission]
    star_queryset = StarItems.objects.filter(is_active=1)

    def get(self, request, col=None):
        serializer = PageSerializer(data=request.GET)
        if serializer.is_valid():
            li, total = Mongo.get_pages(col, **serializer.validated_data)
            if request.user.is_authenticated:
                for i in li:
                    i["is_star"] = self.star_queryset.filter(
                        item_id=i.get("itme_id"), user=request.user
                    ).exists()
            if not settings.DEBUG:
                data = dumps(
                    {
                        "data": li,
                        "code": "200",
                        "msg": "ok",
                        "total": total,
                        "page": serializer.validated_data.get("page"),
                        "pagesize": serializer.validated_data.get("pagesize"),
                    },
                    ensure_ascii=False,
                    default=datetime_serialization_handler,
                )
            else:
                data = aes_encrypt(
                    dumps(
                        {
                            "data": li,
                            "code": "200",
                            "msg": "ok",
                            "total": total,
                            "page": serializer.validated_data.get("page"),
                            "pagesize": serializer.validated_data.get("pagesize"),
                        },
                        ensure_ascii=True,
                        default=datetime_serialization_handler,
                    )
                )
            resp = HttpResponse(data)

            return resp
        else:
            return Resp.failed(msg=serializer.errors)


class GoodsLeaksList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    star_queryset = StarItems.objects.filter(is_active=1)

    def get(self, request, col=None):
        serializer = PageSerializer(data=request.GET)
        if serializer.is_valid():
            if request.user.isvip and request.user.vip >= 5:
                li, total = Mongo.get_leaks(col, **serializer.validated_data)
                if request.user.is_authenticated:
                    for i in li:
                        i["is_star"] = self.star_queryset.filter(
                            item_id=i.get("itme_id"), user=request.user
                        ).exists()
                if not settings.DEBUG:
                    data = dumps(
                        {
                            "data": li,
                            "code": "200",
                            "msg": "ok",
                            "total": total,
                            "page": serializer.validated_data.get("page"),
                            "pagesize": serializer.validated_data.get("pagesize"),
                        },
                        ensure_ascii=False,
                        default=datetime_serialization_handler,
                    )
                else:
                    data = aes_encrypt(
                        dumps(
                            {
                                "data": li,
                                "code": "200",
                                "msg": "ok",
                                "total": total,
                                "page": serializer.validated_data.get("page"),
                                "pagesize": serializer.validated_data.get("pagesize"),
                            },
                            ensure_ascii=True,
                            default=datetime_serialization_handler,
                        )
                    )
                resp = HttpResponse(data)

                return resp
            else:
                return Resp.failed(msg="vip到期,或等级不足vip5")
        else:
            return Resp.failed(msg=serializer.errors)


class GoodsDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomPermission]
    star_queryset = StarItems.objects.filter(is_active=1)

    def get(self, request, item_id=None):
        try:
            li = Mongo.getDetail(item_id)
            if request.user.is_authenticated:
                li["is_star"] = self.star_queryset.filter(
                    item_id=item_id, user=request.user
                ).exists()
            if not settings.DEBUG:
                data = dumps(
                    {"data": li, "code": "200", "msg": "ok"},
                    ensure_ascii=False,
                    default=datetime_serialization_handler,
                )

            else:
                data = aes_encrypt(
                    dumps(
                        {"data": li, "code": "200", "msg": "ok"},
                        ensure_ascii=True,
                        default=datetime_serialization_handler,
                    )
                )
            resp = HttpResponse(data)

            return resp
        except Exception as e:

            return Resp.failed(msg=f"{e}")


class CommentsViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # 搜索
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CommentsFilter
    # search_fields = ('item_id','user__email')
    # # 排序

    ordering_fields = ("create_time", "last_update")
    permission_classes = [CustomPermission]
    queryset = CommentItems.objects.filter(is_active=True)
    serializer_class = CommentsSerializer

    def perform_create(self, serializer):
        # Add a log entry for creating an order
        serializer.validated_data["user"] = self.request.user
        instance = serializer.save()

    def perform_update(self, serializer):
        # Add a log entry for updating an order
        serializer.validated_data["user"] = self.request.user
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 在这里设置逻辑删除的标志，例如修改 is_deleted 字段
        instance.is_active = False
        instance.save()

        return Response(status=200, data={"code": "200", "data": "", "msg": "ok"})

    def list(self, request, *args, **kwargs):
        pagesize = self.paginator.page_size
        if request.user.is_authenticated:
            queryset = self.filter_queryset(self.get_queryset()).annotate(
                is_mine=Case(
                    When(user=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        else:
            queryset = self.filter_queryset(self.get_queryset()).annotate(
                is_mine=Value(False)
            )

        # 分页查询集
        page = self.paginate_queryset(queryset)
        pager = {}
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pager = self.paginator.get_paginated_response(serializer.data)

        # 如果没有分页，直接返回查询集结果
        serializer = self.get_serializer(queryset, many=True)
        # 自定义返回值
        res = []
        for data in pager.data.get("results", []):
            res.append(
                {
                    **user.objects.get(pk=data.pop("user")).to_dict(),
                    **data,
                    **GoodsName.objects.get(item_id=data.pop("item_id")).to_dict(),
                }
            )

        data = {
            "total": queryset.count(),
            "page": pager.data.get("page", 1),
            "pagesize": pagesize,
            "data": res,
        }
        return Response(data)

    @action(detail=False, methods=["DELETE"])
    def delete_many(self, request, *args, **kwargs):
        try:
            ids = request.data.get("ids")
            # 在数据库中删除相应的对象
            queryset = self.queryset.filter(pk__in=ids, user=request.user)
            queryset.update(is_active=False)
            return Resp.success()
        except Exception as e:
            return Resp.failed(msg=str(e))


class StarsViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # 搜索
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StarsFilter
    # search_fields = ('user__email',)
    lookup_field = "item_id"
    # # 排序
    ordering_fields = ("last_update",)
    permission_classes = [CustomPermission2]
    queryset = StarItems.objects.filter(is_active=True)
    serializer_class = StarsSerializer

    def perform_create(self, serializer):
        # Add a log entry for creating an order
        serializer.validated_data["user"] = self.request.user
        instance = serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 在这里设置逻辑删除的标志，例如修改 is_deleted 字段
        instance.is_active = False
        instance.save()
        return Response(status=200, data={"code": "200", "data": "", "msg": "ok"})

    def list(self, request, *args, **kwargs):
        pagesize = self.paginator.page_size
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        # 分页查询集
        page = self.paginate_queryset(queryset)
        pager = {}
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pager = self.paginator.get_paginated_response(serializer.data)

        # 如果没有分页，直接返回查询集结果
        serializer = self.get_serializer(queryset, many=True)
        # 自定义返回值
        res = []
        item_ids = [data["item_id"] for data in pager.data.get("results", [])]
        details = Mongo.get_items("buff_csgo", item_ids)
        for index, data in enumerate(pager.data.get("results", [])):
            item_id = data.pop("item_id")
            detail = details[index]  # 获取对应item_id的数据
            detail.pop("_id", None)
            detail.pop("update_time", None)
            detail.pop("create_time", None)
            res.append({**detail, **data})

        data = {
            "total": queryset.count(),
            "page": pager.data.get("page", 1),
            "pagesize": pagesize,
            "data": res,
            "code": "200",
        }
        return Response(data)

    @action(detail=False, methods=["DELETE"])
    def delete_many(self, request, *args, **kwargs):
        try:
            ids = request.data.get("ids")
            # 在数据库中删除相应的对象
            queryset = self.queryset.filter(item_id__in=ids, user=request.user)
            queryset.update(is_active=False)
            return Resp.success()
        except Exception as e:
            return Resp.failed(msg=str(e))

    @action(detail=True, methods=["POST"])
    def addStar(self, request, item_id=None, *args, **kwargs):
        if item_id:
            star_item=StarItems.objects.filter(item_id=item_id,
                user=request.user)
            
            # 如果记录已存在，则自增 count 字段的值
            if not star_item.exists():
                star_item=StarItems.objects.create(item_id=item_id,
                user=request.user,is_active=True)
                # 使用 F() 表达式自增字段值
                star_item.save()
            else:
                star_item=star_item.first()
                star_item.is_active=not star_item.is_active
                star_item.save()
            return Response({"code": "200", "data": star_item.is_active, "msg": "ok"})
        else:

            return Response({"code": "500", "data": "", "msg": "item_id是必要参数"})


class ClicksViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # 搜索
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClickFilter
    search_fields = ("item_id",)
    lookup_field = "item_id"
    # # 排序
    ordering_fields = ("last_update",)
    permission_classes = [CustomPermission2]
    queryset = ClickItems.objects.filter(is_active=True)
    serializer_class = ClicksSerializer

    def perform_create(self, serializer):
        # Add a log entry for creating an order
        serializer.validated_data["user"] = self.request.user
        instance = serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 在这里设置逻辑删除的标志，例如修改 is_deleted 字段
        instance.is_active = False
        instance.save()
        return Response(status=200, data={"code": "200", "data": "", "msg": "ok"})

    @action(detail=False, methods=["DELETE"])
    def delete_many(self, request, *args, **kwargs):
        try:
            ids = request.data.get("ids")
            # 在数据库中删除相应的对象
            queryset = self.queryset.filter(item_id__in=ids, user=request.user)
            queryset.update(is_active=False)
            return Resp.success()
        except Exception as e:
            return Resp.failed(msg=str(e))

    def list(self, request, *args, **kwargs):
        pagesize = self.paginator.page_size
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        # 分页查询集
        page = self.paginate_queryset(queryset)
        pager = {}
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pager = self.paginator.get_paginated_response(serializer.data)

        # 如果没有分页，直接返回查询集结果
        serializer = self.get_serializer(queryset, many=True)
        # 自定义返回值
        res = []
        item_ids = [data["item_id"] for data in pager.data.get("results", [])]
        details = Mongo.get_items("buff_csgo", item_ids)
        for index, data in enumerate(pager.data.get("results", [])):
            item_id = data.pop("item_id")
            detail = details[index]  # 获取对应item_id的数据
            detail.pop("_id", None)
            detail.pop("update_time", None)
            detail.pop("create_time", None)
            res.append({**detail, **data})
        data = {
            "total": queryset.count(),
            "page": pager.data.get("page", 1),
            "pagesize": pagesize,
            "data": res,
            "code": "200",
        }
        return Response(data)

    @action(detail=True, methods=["POST"])
    def addClick(self, request, item_id=None, *args, **kwargs):
        if item_id:
            defaults = {
                "item_id": item_id,
                "user": request.user,
                "is_active": True,
            }

            click_item, created = ClickItems.objects.update_or_create(
                item_id=item_id,
                user=request.user,
                defaults=defaults,
            )

            # 如果记录已存在，则自增 count 字段的值
            if not created:
                click_item.count = F("count") + 1  # 使用 F() 表达式自增字段值
                click_item.save()
            else:
                click_item.count = 1  # 使用 F() 表达式自增字段值
                click_item.save()
            return Response({"code": "200", "data": "", "msg": "ok"})
        else:

            return Response({"code": "500", "data": "", "msg": "item_id是必要参数"})
