import re

raw_key = '''-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDmt9sdu5rh//IkrjRG+G6Qb5t8sgS+JQckEqel+NkPyHvxyAA
BdlTVjWYWaLF7FTkISnY/lVNDC5MN78qlJDWQ2lMf/JQD5wcZEvckQ+rHOKYnU/f
VdWB2MAQUdhx8OteY3qY2j4P6IYr6XKZdcNDIlAqI4V6vEFRsiZd769MxwIDAQAB
AoGBAKiLP2LlHixjUX1CVDc0ap4qUPb5GPfi6DBFqH1a8B7Xj+8eRF4/55ddryFw
udxk3U8aevuumMjpsf5XmU5zDk1nQKAOXQVk2ytKsV/iULXO/vN1lBdkxrfqbdab1
WkRiCiFYDVAUPB+Bpv2X6yGW5HXZ5FxeVSj/hA7b3FMhvGEhAkEA82vfyi9mBu3f
mPj3cuSl3caPReVfku7V3pDYdOf9L1mUsX+L2u6B2LkQ8dBC2H8TG9W/T4plYJGX
yXGG1JCnawJBAPKj76ej0AvIIZen/siJ5pGrkS5VJDMGQt23AF1vc8VHFLF+9Be8
RkWqasYjFu3/T/efaE+prpqQL82nekd18xUCQQCnGsDwjYVe8GF1JETK7Mgo7Sxh
8UqhFbBgL9NIvhGDNd3r1AFwdBdTbgiB2FRrRyEZFK1Wr01U893dfj/vILatAkBj
wnUpJpfGEE2HbeG6D8CFidWSCB1vARcC01fKEqW1qYjfhUPUcmst/2gQ+KJXzc3S
EG8xuaD5GWke8qzKOwVAkEAtCDwOvRz6NCYhvavbtM4ZTX/I1Cri2di2BusYzBL
xmRS2GgLAZOsQyIW738Rc1MB8r4vu94gKQTPgKdbyw+NJw==
-----END RSA PRIVATE KEY-----'''

# 1. 提取中间的核心字母（过滤掉头尾和所有不可见字符）
b64_part = re.sub(r'[^a-zA-Z0-9+/=]', '', raw_key.replace("-----BEGIN RSA PRIVATE KEY-----", "").replace("-----END RSA PRIVATE KEY-----", ""))

print(f"🔍 当前提取到的字符数: {len(b64_part)}")

# 2. 标准校验
if len(b64_part) == 816:
    print("✅ 长度完美！格式 100% 正确，可以拿去解密了。")
elif len(b64_part) == 812:
    print("⚠️ 少了个等于号（=），请在末尾手动补上 `==`")
elif len(b64_part) > 816:
    print(f"❌ 多了 {len(b64_part) - 816} 个字符。可能有拼写重复。")
elif len(b64_part) < 816:
    print(f"❌ 少了 {816 - len(b64_part)} 个字符。OCR 漏掉了一部分数据。")
