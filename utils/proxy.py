'''proxy的数据类，用于统一proxy数据格式'''

import re
from utils.mylog import Logger


logger = Logger('Proxy')

class Proxy:
    def __init__(self,host='0.0.0.0',port='0000'):
        self.host = host
        self.port = port

    def value(self):
        return f'{self.host}:{self.port}'

    @classmethod
    def from_string(cls,string):
        try:
            host,port=re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)',string).groups()
            return cls(host,port)
        except:
            logger.log('ERROR',f'{str}从字符串创建失败Proxy失败，已返回默认值')
            return cls()

    def __repr__(self):
        return f'Proxy({self.host}:{self.port})'



if __name__=='__main__':
    proxy=Proxy.from_string('hhh127.0.0.1:8080')
    print(proxy.value())
