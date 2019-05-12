import pickle, base64


def dumps(dict1):
    # 字典转为字节类型的字符串
    pickle_bstr = pickle.dumps(dict1)
    # 字节编码
    bstr = base64.b64encode(pickle_bstr)
    # 字节转为字符串
    str1 = bstr.decode()
    return str1


def loads(str1):
    # 字符串转为字节
    bstr = str1.encode()
    # 字节解码
    pickle_bstr = base64.b64decode(bstr)
    # 字节转为字典
    dict1 = pickle.loads(pickle_bstr)
    return dict1
