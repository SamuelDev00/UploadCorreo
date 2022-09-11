class ProxyCloud(object):
    def __init__(self, ip,port,type='socks5'):
        self.ip = ip
        self.port = port
        self.default = None
        self.type = type
    def set_default (self,socket):
        self.default = socket
    def as_dict_proxy(self):
        return {'http':f'{self.type}://'+self.ip+':'+str(self.port)+'',
                'https':f'{self.type}://'+self.ip+':'+str(self.port)+''}
    def to_socks5(self):
        return f'socks5://{self.ip}:{self.port}'

def parse(text):
    try:
        tokens = str(text).split('://')
        type = tokens[0]
        proxy_tokens = str(tokens[1]).split(':')
        ip = proxy_tokens[0]
        port = int(proxy_tokens[1])
        return ProxyCloud(ip,port,type)
    except:pass
    return None

