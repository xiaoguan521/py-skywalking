import requests
import pandas as pd
from datetime import datetime,timezone
from requests.auth import HTTPBasicAuth

# Skywalking API 端点
SKYWALKING_API_URL = "http://34.92.247.5/graphql" # 替换为实际的 API 地址

# Basic Auth 用户名和密码
USERNAME = "skywalking"  # 替换为实际用户名
PASSWORD = "skywalking"  # 替换为实际密码

# 查询服务的函数
def query_services(duration, keyword):
    query = """
    query queryServices($duration: Duration!, $keyword: String!) {
        services: getAllServices(duration: $duration, group: $keyword) {
            key: id
            label: name
            group
        }
    }
    """
    variables = {
        "duration": duration,
        "keyword": keyword
    }
    response = requests.post(SKYWALKING_API_URL, json={"query": query, "variables": variables}, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return response.json().get('data', {}).get('services', [])

# 查询追踪的函数
def query_traces(condition):
    query = """
    query queryBasicTraces($condition: TraceQueryCondition) {
        queryBasicTraces(condition: $condition) {
            traces {
                key: segmentId
                endpointNames
                duration
                start
                isError
                traceIds
            }
        }
    }
    """
    response = requests.post(SKYWALKING_API_URL, json={"query": query, "variables": condition}, auth=HTTPBasicAuth(USERNAME, PASSWORD))
   
    return response.json().get('data', {}).get('queryBasicTraces', {}).get('traces', [])

# 主函数
def main():
    # 定义查询参数
    duration = {
        "start": "2024-09-29 20",
        "end": "2024-09-29 21",
        "step": "HOUR"
    }
    
    keyword = "agent"
    
    # 查询服务
    services = query_services(duration, keyword)
    results = []

    for service in services:
        service_id = service['key']
       
        # 定义追踪查询条件s
        condition = {
             "condition": {  # 添加外层的 condition 字段
                "queryDuration": {
                    "start": "2024-09-29 1411",  # 替换为实际的开始时间
                    "end": "2024-09-29 1441",    # 替换为实际的结束时间
                    "step": "MINUTE"
                },
                "traceState": "ALL",
                "paging": {
                    "pageNum": 1,
                    "pageSize": 100  # 可以根据需要调整每页的大小
                },
                "queryOrder": "BY_START_TIME",
                "serviceId": service_id  # 使用服务 ID 查询追踪数据
             }
        }
        # 查询追踪数据并收集结果
        traces = query_traces(condition)
        # print(traces)
        for trace in traces:
            for endpoint in trace.get('endpointNames', []):
                results.append({
                    "service_name": service['label'],
                    "endpoint_name": endpoint,
                    "duration_ms": trace['duration'],  # 响应时间（毫秒）
                    "start_time": datetime.fromtimestamp(float(trace['start'])/1000.0).strftime('%Y-%m-%d %H:%M:%S'),  # 转换为可读格式                    
                    "is_error": trace['isError']
                })
    # 保存结果为 Excel 文件
    df = pd.DataFrame(results)
    df.to_excel("skywalking_traces.xlsx", index=False)

if __name__ == "__main__":
    main()