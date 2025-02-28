'''代理池实现模块，主要实现爬取与测试逻辑'''

from scr.spiders import *
from utils.my_redis import RedisPool
from config.setting import Test_Url,Test_Cycle,Fetch_Cycle,Test_Count
from utils.mylog import Logger


class ProxyPool:
    def __init__(self,redis=None,test_cycle=Test_Cycle,fetch_cycle=Fetch_Cycle):
        self.redis = redis or RedisPool()
        self.logger = Logger(self.__class__.__name__)
        self.test_spider=TestSpider(semaphore=asyncio.Semaphore(500)) #控制一下并发量，不然redis会崩
        self.test_cycle=test_cycle
        self.fetch_cycle=fetch_cycle
        self.fetch_spiders=[FreeProxySpider1(),FreeProxySpider2(),FreeProxySpider3(),FreeProxySpider4(),FreeProxySpider5(),FreeProxySpider6(),FreeProxySpider7()]

    async def _set_proxy_score(self,proxy:str,test_url=Test_Url,n=Test_Count):
        sc=0
        responses=await asyncio.gather(*[self.test_spider.test(url=test_url, proxy=proxy) for _ in range(n)])
        for response in responses:
            if response.status == 200:
                sc+=1
        await self.redis.filter(proxy, sc/n)

    async def test(self,test_url=Test_Url):
        await asyncio.sleep(20) #先让爬虫爬一些代理
        while True:
            self.logger.log('INFO', '开始检测')
            await asyncio.gather(*[self._set_proxy_score(proxy.decode('utf-8'),test_url) for proxy in await self.redis.get_all()])

            count=await self.redis.redis.zcount(self.redis.zset_name,0,1)
            self.logger.log('INFO',f'检测完毕，还剩{count}个代理')
            await asyncio.sleep(Test_Cycle)

    async def _fetch_by_sigspider(self,spider:BaseSpider):
        async for fetch_proxy in spider.fetch():
            await self.redis.add(fetch_proxy)

    async def fetch(self):
        while True:
            self.logger.log('INFO', '开始采集')
            fetch_tasks=[self._fetch_by_sigspider(spider) for spider in self.fetch_spiders]
            await asyncio.gather(*fetch_tasks, return_exceptions=True)
            await asyncio.sleep(Fetch_Cycle)

    async def run(self):
        try:
            await asyncio.gather(self.fetch(),self.test())
        finally:
            await self.close()

    async def close(self):
        close_tasks = [spider.close() for spider in self.fetch_spiders]
        close_tasks.append(self.test_spider.close())
        await asyncio.gather(*close_tasks)


if __name__ == '__main__':
    # 测试使用
    async def main():
        proxypool=ProxyPool()
        await proxypool.run()

    asyncio.run(main())




