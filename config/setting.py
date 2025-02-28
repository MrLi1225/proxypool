
# 储存模块配置
Redis_Url=r'redis://:password@127.0.0.1:6379/0' # 替换为自己的redis连接链接
Initial_Score=0

Test_Cycle=60*5 # 测试周期，单位秒
Fetch_Cycle=60*10 # 爬取周期，单位秒

# 测试模块设置
Test_Url=r'https://www.huodongxing.com'
Test_Count=5 # 单次测试时对单个代理的测试总次数，分数记为：成功次数/总次数
Del_Score=0.1 # 低于该分数的代理将会删除

# 爬取模块设置
Concurrent_Limit=100 # 单次爬取代理的并发限制

# 服务接口设置
Api_Host='127.0.0.1'
Api_Port=5000



