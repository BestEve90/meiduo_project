from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall.settings.dev import SECRET_KEY


def generate_access_token(data_dict, expire):
    serializer = Serializer(SECRET_KEY, expire)
    # serializer.dumps(数据), 返回bytes类型
    token = serializer.dumps(data_dict)
    token = token.decode()
    return token


def check_access_token(token,expire):
    # 检验token
    # 验证失败，会抛出itsdangerous.BadData异常
    serializer = Serializer(SECRET_KEY, expire)
    try:
        data_dict = serializer.loads(token)
    except:
        return None
    return data_dict


if __name__ == '__main__':
    token = generate_access_token({'hello':1234566},5)
    print(check_access_token(token,10))
