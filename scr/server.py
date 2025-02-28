'''接口模块，实现基于FastAPI的api接口'''

from fastapi import FastAPI
import uvicorn

from utils.my_redis import RedisPool
from config.setting import Api_Host,Api_Port

app = FastAPI()
redis = RedisPool()
@app.get('/')
def index():
    return '<h2>这是我的第一个代理池</h2>'

@app.get('/get_proxy')
async def get_proxy():
    return await redis.get_proxy()

@app.get('/get_proxy/best')
async def get_best_proxy():
    return await redis.get_best_proxy()

@app.get('/random')
async def get_proxy(min_sc: float=0.3, max_sc: float=1,withsc=False):
    return await redis.get_random_proxy(min_score=min_sc, max_score=max_sc, withsc=withsc)


def run_server():
    uvicorn.run(app, host=Api_Host, port=Api_Port)


if __name__ == '__main__':
    run_server()


