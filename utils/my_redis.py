'''redis异步框架的简单包装，用途有二：1.作为工具类服务于ProxyPool类；2.实现api接口逻辑'''

import asyncio
import redis.asyncio as redis
import random

from config.setting import Redis_Url,Initial_Score,Del_Score
from utils.mylog import Logger
from utils.proxy import Proxy


class RedisPool(object):

    def __init__(self,redis_url=Redis_Url,zset_name = 'proxy_pool'):
        self.redis_url = redis_url
        self.logger = Logger(self.__class__.__name__)
        self.redis = redis.from_url(redis_url)
        self.zset_name = zset_name

    async def add(self,proxy:Proxy):
        if await self.redis.zadd(self.zset_name, {proxy.value():Initial_Score}, nx=True):
            self.logger.log('DEBUG', f'已采集{proxy.value()}')
        else:
            self.logger.log('DEBUG', f'已存在{proxy.value()}')

    async def get_all(self):
        return await self.redis.zrange(self.zset_name, 0, -1)

    async def filter(self,proxy:str,score:float):
        if score <= Del_Score:
            await self.redis.zrem(self.zset_name,proxy)
            self.logger.log('DEBUG',f'已删除代理:{proxy}，分数:{score}')
            return False
        else:
            await self.redis.zadd(self.zset_name, {proxy:score})
            self.logger.log('DEBUG',f'已设置代理分数:{proxy},分数:{score}')
            return True

    async def get_proxy(self):
        return await self.redis.zrevrange(self.zset_name, 0, -1, withscores=True)

    async def get_random_proxy(self,min_score:float,max_score:float,withsc=False):
        data= await self.redis.zrangebyscore(self.zset_name, min_score, max_score, withscores=withsc)
        return random.choice(data)

    async def get_best_proxy(self):
        elements_with_scores = await self.redis.zrevrange(self.zset_name, 0, -1, withscores=True)
        highest_score = elements_with_scores[0][1]

        # 筛选出所有具有最高分数的元素
        highest_elements = [elem[0] for elem in elements_with_scores if elem[1] == highest_score]

        # 从所有最高分数的元素中随机选择一个
        random_element = random.choice(highest_elements)
        return random_element


if __name__ == '__main__':
    '''调试模块'''
    async def main():
        pool = RedisPool()
        print(await pool.get_best_proxy())

    asyncio.run(main())