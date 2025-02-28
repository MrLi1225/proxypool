'''response数据类，主要用于储存aiohttp的response,从而释放并发信号量，避免卡死'''

from dataclasses import dataclass
from typing import Optional


@dataclass
class Response:
    status: int             # HTTP 状态码
    text: str               # 响应的文本内容
    json: Optional[dict] = None  # 可选的 JSON 数据

    @classmethod
    async def from_response(cls, response):
        status = response.status
        text = await response.text('utf-8', 'ignore')
        try:
            json_data = await response.json(content_type=None)
        except:
            json_data = None
        return cls(status=status, text=text, json=json_data)

    @classmethod
    def get_default(cls):
        return cls(status=0, text='', json=None)


