from qiniu import Auth, put_data
from flask import current_app

#def put_qiniu():
#    """上传图片到七牛云"""
#    access_key = Config.QINIU_AK
#    secret_key = Config.QINIU_SK
#    q = Auth(access_key, secret_key)
#    bucket_name = 'Bucket_Name'
#    key = 'my-python-logo.png';
#    #上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
#    policy={
#             'callbackUrl':'http://your.domain.com/callback.php',
#              'callbackBody':'filename=$(fname)&filesize=$(fsize)'
#               }
#    token = q.upload_token(bucket_name, key, 3600, policy)
#    localfile = './sync/bbb.jpg'
#    ret, info = put_file(token, key, localfile)
#    print(info)
#    assert ret['key'] == key
#    assert ret['hash'] == etag(localfile)
#    return ret

def upload_pic(f1):
    # f1表示接收的浏览器传递的文件对象
    access_key = current_app.config.get("QINIU_AK")
    secret_key = current_app.config.get("QINIU_SK")
    # 空间名称
    bucket_name = current_app.config.get("QINIU_BUCKET")
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 生成上传 Token
    token = q.upload_token(bucket_name)
    # 上传文件数据，ret是字典，键为hash、key，值为新文件名，info是response对象
    ret, info = put_data(token, None, f1.read())
    # 返回七牛云给出的文件名
    return ret.get('key')
