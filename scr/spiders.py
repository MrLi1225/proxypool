'''爬虫模块，实现对各个网站代理爬取的逻辑，实现完记得在ProxyPool类的init中注册'''

from utils.spider_base import BaseSpider
import asyncio
import re
from playwright.async_api import async_playwright
import aiohttp

from utils.proxy import Proxy
from utils.response import Response


class TestSpider(BaseSpider):
    '''测试专用类'''

    async def test(self,url,proxy):
        await asyncio.sleep(1)
        try:
            return await self._sent_request(url, proxy)

        except aiohttp.ClientProxyConnectionError:
            self.logger.log('DEBUG',f"代理连接失败: {proxy}")

        except aiohttp.ClientHttpProxyError:
            self.logger.log('DEBUG',f"代理 HTTP 代理错误: {proxy}")
        except aiohttp.ServerDisconnectedError:
            self.logger.log('DEBUG',f"代理服务器断开连接: {proxy}")
        except aiohttp.ClientConnectorError:
            self.logger.log('DEBUG',f"代理连接错误: {proxy}")
        except asyncio.TimeoutError:
            self.logger.log('DEBUG',f"代理超时: {proxy}")
        except aiohttp.ClientResponseError as e:
            self.logger.log('DEBUG',f"目标站点返回错误 {e.status}: {proxy}")
        except Exception as e:
            self.logger.log('ERROR',f"其他错误 {type(e).__name__}: {proxy} -> {e}")

        return Response(status=0, text='', json=None)


class FreeProxySpider1(BaseSpider):
    # 89免费代理 https://www.89ip.cn/api.html
    url=r'http://api.89ip.cn/tqdl.html?api=1&num=100&port=&address=&isp='
    p=None

    async def _sent_request(self, url, proxy=None,*pargs,**kwargs):
        if self.p is None:
            self.p = await async_playwright().start()
            self.browser = await self.p.chromium.launch(headless=True)
        page = await self.browser.new_page()
        status=[] #第一个状态码为521，第二个才是所需要的页面
        page.on("response", lambda response, st=status: st.append(response.status))

        await page.goto(self.url,timeout=60000)
        for _ in range(3): #这个网站有反爬策略，会连续发起4个请求，第二个是我们所需要的
            await page.wait_for_load_state(timeout=60000)
            await page.wait_for_timeout(1000)
        page_source = await page.content()
        if status:
            if status[0]==502:
                await page.close()
                response= await self._sent_request(url, proxy=proxy)
            else:
                response=Response(status=status[1], text=page_source, json=None)
                await page.close()
            return response
        else:
            await page.close()
            self.logger.log('EEROR',f'{self.url}无状态码')
            raise ValueError

    async def fetch(self):
        response = await self.get_response(self.url)
        home_url = r'https://www.89ip.cn/'
        if response.status == 521:
            await self.get_response(home_url)
            response = await self.get_response(self.url)
        async for proxy in self.parse(response):
            yield proxy

    async def close(self):
        await super().close()
        if self.p:
            await self.browser.close()
            await self.p.stop()


class FreeProxySpider2(BaseSpider):
    # 齐云代理 https://proxy.ip3366.net/free
    url=r'https://proxy.ip3366.net/free'

    async def parse(self,response):
        datas = re.findall(r'<td data-title="IP">([\d\.]*)</td>.*?<td data-title="PORT">(\d+)</td>', response.text,flags=re.S)
        for host,port in datas:
            yield Proxy(host=host,port=port)

    async def fetch(self):
        for i in range(1,8):
            url=self.url+f'?page={i}'
            response = await self.get_response(url)
            async for proxy in self.parse(response):
                yield proxy


class FreeProxySpider3(BaseSpider):
    #云代理 http://www.ip3366.net/free/?stype=1
    url=r'http://www.ip3366.net/free'

    async def parse(self,response):
        datas = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>.*?<td>(\d+)</td>', response.text,
                           flags=re.S)
        for host, port in datas:
            yield Proxy(host=host, port=port)

    async def fetch(self):
        for page in range(1,7):
            for stype in [1,2]:
                url=self.url+f'/?stype={stype}&page={page}'
            response = await self.get_response(self.url)
            async for proxy in self.parse(response):
                yield proxy


class FreeProxySpider4(BaseSpider):
    # 稻壳代理 https://www2.docip.net/data/free.json
    url=r'https://www2.docip.net/data/free.json'

    async def parse(self,response):
        for data in response.json['data']:
            yield data['ip']

    async def fetch(self):
        response = await self.get_response(self.url)
        async for proxy in self.parse(response):
            yield Proxy.from_string(proxy)


class FreeProxySpider5(BaseSpider):
    # ipipgo帖子 https://www.ipipgo.com/ipdaili/16926.html
    url=r'https://www.ipipgo.com/ipdaili/16926.html'

    async def fetch(self):
        response = await self.get_response(self.url)
        async for proxy in self.parse(response):
            yield proxy


class FreeProxySpider6(BaseSpider):
    # proxy5 https://proxy5.net/cn/free-proxy/china
    url=r'https://proxy5.net/cn/free-proxy/china'

    async def parse(self,response):
        datas = re.findall(r'<td><strong>(\d+\.\d+\.\d+\.\d+)</strong></td>.*?<td>(\d+)</td>', response.text,
                           flags=re.S)
        for host, port in datas:
            yield Proxy(host=host, port=port)

    async def fetch(self):
        response = await self.get_response(self.url)
        async for proxy in self.parse(response):
            yield proxy
        nonce=re.findall(r',"nonce":"(.*?)"',response.text)[0]

        async def parse_next(page,rs,nonce=nonce):
            post_url = 'https://proxy5.net/wp-admin/admin-ajax.php'
            data = {
                'action': 'proxylister_load_more',
                'nonce': nonce,
                'page': page,
                'atts[country]': 'China',
                'atts[sort_by]': '-uptime',
            }
            response = await self.get_response(post_url, data=data, mode='post')
            if response.status == 403:
                return
            datas = re.findall(r'<td><strong>(\d+\.\d+\.\d+\.\d+)</strong></td>.*?<td>(\d+)</td>',
                               response.json['data']['rows'],
                               flags=re.S)
            for host, port in datas:
                rs.append( Proxy(host=host, port=port))
        max_page=40
        rs=[]
        await asyncio.gather(*[parse_next(page,rs) for page in range(1,max_page)])
        for proxy in rs:
            if proxy:
                yield proxy


class FreeProxySpider7(BaseSpider):
    # 快代理 https://www.kuaidaili.com/free/dps/1/
    url=r'https://www.kuaidaili.com/free/dps/'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    async def parse(self,response):
        datas=re.findall(r'"ip": "(\d+\.\d+\.\d+\.\d+)".*?"port": "(\d+)"}',response.text,flags=re.S)
        for host, port in datas:
            yield Proxy(host=host, port=port)

    async def fetch(self):
        for i in range(1, 20):
            await asyncio.sleep(0.5)
            url = self.url + str(i)
            response = await self.get_response(url)
            async for proxy in self.parse(response):
                yield proxy




if __name__ == '__main__':
    '''调试代码'''
    async def main1():
        spider = FreeProxySpider6()
        await spider.fetch()

    async def main2():
        spider = FreeProxySpider6()
        async for proxy in spider.fetch():
            print(proxy)

    async def test():
        spider =TestSpider()
        r=await spider.test(r'https://www.huodongxing.com','139.129.166.68:3128')
        print(r)


    asyncio.run(main2())

