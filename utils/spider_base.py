'''基于aiohttp的爬虫基类，实现通用爬虫逻辑'''

import aiohttp
import asyncio
from fake_useragent import UserAgent
import re

from utils.proxy import Proxy
from utils.mylog import Logger
from utils.response import Response
from config.setting import *

ua = UserAgent()

class BaseSpider:
    url=r''
    headers={'User_Agent':ua.random}

    def __init__(self,cookies=None,semaphore=None):
        self.semaphore =semaphore or asyncio.Semaphore(Concurrent_Limit)
        self.session = aiohttp.ClientSession(cookies=cookies,headers=self.headers,connector=aiohttp.TCPConnector(ssl=False),timeout=aiohttp.ClientTimeout(30)) if cookies else aiohttp.ClientSession(headers=self.headers,connector=aiohttp.TCPConnector(ssl=False),timeout=aiohttp.ClientTimeout(30))
        self.logger = Logger(self.__class__.__name__)

    @staticmethod
    def get_user_agent():
        return ua.random

    async def _sent_request(self,url,proxy=None,mode='get',data=None,*pargs,**kwargs):
        r=Response.get_default()
        async with self.semaphore:
            if proxy:
                if url.startswith('http'):
                    proxy = 'http://' + proxy
                else:
                    self.logger.log('ERROR','未设置该url的代理模式')

                if mode == 'get':
                    async with self.session.get(url, proxy=proxy) as response:
                        r=await Response.from_response(response)

                elif mode == 'post':
                    async with self.session.post(url, proxy=proxy,data=data) as response:
                        r=await Response.from_response(response)

            else:
                if mode == 'get':
                    async with self.session.get(url) as response:
                        r = await Response.from_response(response)

                elif mode == 'post':
                    async with self.session.post(url, proxy=proxy,data=data) as response:
                        r = await Response.from_response(response)
            return r

    async def get_response(self,url,proxy=None,retry_n=3,mode='get',data=None):
        for i in range(retry_n):
            try:
                response=await self._sent_request(url, proxy=proxy, mode=mode, data=data)
                if response.status != 200:
                    self.logger.log('DEBUG', f'{url}第{i}次爬取失败，状态码：{response.status}')
                    continue
                return response
            except Exception as e:
                self.logger.log('DEBUG',f'url:{url}爬取失败:{e}')
                await asyncio.sleep(2**i)
        return Response(status=0, text='', json=None)

    async def parse(self,response):
        proxies = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', response.text)
        for proxy in proxies:
            yield Proxy.from_string(proxy)

    async def close(self):
        await self.session.close()

    async def fetch(self):
        '''需实现yield Proxy对象'''
        yield Proxy()








