from utils.ytx_sdk.CCPRestSDK import REST


accountSid = '8aaf0708639129c40163a0bb54e10a04';
# 说明：主账号，登陆云通讯网站后，可在控制台首页中看到开发者主账号ACCOUNT SID。

accountToken = '6e42eda77c2f4924a23ce445a04de264';
# 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN。

appId = '8aaf0708639129c40163a1bfdcd50cda';
# 请使用管理控制台中已创建应用的APPID。

serverIP = 'app.cloopen.com';
# 说明：请求地址，生产环境配置成app.cloopen.com。

serverPort = '8883';
# 说明：请求端口 ，生产环境为8883.

softVersion = '2013-12-26';  # 说明：REST API版本号保持不变。

def sendTemplateSMS(to, datas, tempId):
    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    return result.get('statusCode')