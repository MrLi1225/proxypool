'''代理池启动入口'''

import asyncio
import multiprocessing

from scr.proxypool import ProxyPool
from scr.server import run_server


def run_proxypool():
    async def init():
        proxypool = ProxyPool()
        await proxypool.run()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init())

def run():
    processes=[multiprocessing.Process(target=run_server), multiprocessing.Process(target=run_proxypool)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    run()





