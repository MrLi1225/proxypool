# 一个简单的代理池项目
---
### 配置
1. 要自行配置好Redis
2. 在config下的setting.py文件中配置Redis的连接url
3. 其他配置依情况自行修改

### 运行
1. 配置完成后运行scr目录下的run.py即可
2. 运行后通过api调用获取代理，默认接口为：http://127.0.0.1:5000

### 接口说明
- **get_proxy**： 获得代理池中的所有代理。
- **/get_proxy/best**： 随机返回一个代理池分数最高的代理。
- **/random？min_sc=0.3&max_sc=1&withsc=false**： 随机返回一个分数处于min_sc与max_sc之间的代理，withsc控制是否返回分数。
