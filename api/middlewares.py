from django.http import HttpResponseForbidden
from .utils.encrypt import Sign,get_params
from django.conf import settings
import json
class NotSpiderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request,item_id):
        user_agent = request.headers.get('User-Agent', '')
        if 'web-crawler' in user_agent:
            return HttpResponseForbidden("Access not allowed.1")
        elif 'headless' in user_agent:
            return HttpResponseForbidden("Access not allowed.2")
        elif not user_agent:
            return HttpResponseForbidden("access not allowed.3")
        referer = request.headers.get('Referer', '')
        allowed_referer = settings.ALLOW_REFERER
        if allowed_referer not in referer and 'servicewechat.com' not in referer and '127.0.0.1' not in referer:
            return HttpResponseForbidden("Access not allowed.4")
        
        header_sign = request.headers.get('sign', '')
        if request.method=='GET':
            sign=Sign(request.path+get_params(request.GET))
        else:
            sign=Sign(request.path+get_params(json.loads(request.body)))
        if sign !=header_sign :
            return HttpResponseForbidden("Access not allowed.5")
        response = self.get_response(request,item_id)
        return response
class NotSpiderMiddleware2:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request,col):
        user_agent = request.headers.get('User-Agent', '')
        if 'web-crawler' in user_agent:
            return HttpResponseForbidden("Access not allowed.1")
        elif 'headless' in user_agent:
            return HttpResponseForbidden("Access not allowed.2")
        elif not user_agent:
            return HttpResponseForbidden("access not allowed.3")
        referer = request.headers.get('Referer', '')
        allowed_referer = settings.ALLOW_REFERER
        if allowed_referer not in referer and 'servicewechat.com' not in referer and '127.0.0.1' not in referer:
            return HttpResponseForbidden("Access not allowed.4")

        header_sign = request.headers.get('sign', '')
        if request.method=='GET':
            sign=Sign(request.path+get_params(request.GET))
        else:
            sign=Sign(request.path+get_params(json.loads(request.body)))
        if sign !=header_sign :
            return HttpResponseForbidden("Access not allowed.5")
        response = self.get_response(request,col)
        return response
class NotSpiderMiddlewareDefualt:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.headers.get('User-Agent', '')
        if 'web-crawler' in user_agent:
            return HttpResponseForbidden("Access not allowed.1")
        elif 'headless' in user_agent:
            return HttpResponseForbidden("Access not allowed.2")
        elif not user_agent:
            return HttpResponseForbidden("access not allowed.3")
        referer = request.headers.get('Referer', '')
        allowed_referer = settings.ALLOW_REFERER
        if allowed_referer not in referer and 'servicewechat.com' not in referer and '127.0.0.1' not in referer:
            return HttpResponseForbidden("Access not allowed.4")

        header_sign = request.headers.get('sign', '')
        if request.method=='GET':
            sign=Sign(request.path+get_params(request.GET))
        else:
            sign=Sign(request.path+get_params(json.loads(request.body)))
        if sign !=header_sign :
            return HttpResponseForbidden("Access not allowed.5")
        response = self.get_response(request)
        return response

