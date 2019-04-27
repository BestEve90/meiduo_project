from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from identify import constants
from meiduo_mall.settings.dev import SECRET_KEY


def generate_access_token(openid):
    serializer = Serializer(SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # serializer.dumps(数据), 返回bytes类型
    token = serializer.dumps({'openid': openid})
    token = token.decode()
    return token


def check_access_token(token):
    # 检验token
    # 验证失败，会抛出itsdangerous.BadData异常
    serializer = Serializer(SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
        openid = data.get('openid')
    except Exception as e:
        return None
    return openid


if __name__ == '__main__':
    token = generate_access_token(1234566)
    print(check_access_token(token))
