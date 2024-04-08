from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import datetime
import hashlib,base64

# 使用 AES 加密
key = b'0123456789abcdef'
def aes_encrypt( data):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(data.encode('utf8'), AES.block_size))
    return base64.b64encode(iv + ciphertext)

def aes_decrypt(data):
    data = base64.b64decode(data)
    iv = data[:AES.block_size]
    ciphertext = data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_data.decode('utf8')
def datetime_serialization_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def get_params(params):
    if not params:
        return ''
    s=[]
    for k,v in params.items():
        s.append(f'{k}={v}')
    return '?'+'&'.join(s)


def Sign(url):
    md5 = hashlib.md5()
    # 更新 MD5 对象以处理要加密的字符串
    md5.update(url.encode('utf-8'))
    # 获取加密后的结果
    md5_str = md5.hexdigest()
    return md5_str
