from rest_framework.response import Response

class Resp:
    @staticmethod
    def success(data=None,code="200",msg="ok",**params)->Response:
        return Response({**{
        "data":data,
        "code":code,
        "msg":msg
        },**params})

    @staticmethod
    def failed(data=None,code="500",msg="error",**params)->Response:
        return Response({**{
        "data":data,
        "code":code,
        "msg":msg
        },**params})