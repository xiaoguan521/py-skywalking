import requests
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, as_completed

# Skywalking API 端点
SKYWALKING_API_URL = "http://34.92.247.5/graphql"

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
    response = requests.post(SKYWALKING_API_URL, json={"query": query, "variables": variables})
    return response.json().get('data', {}).get('services', [])

# 查询实例的函数
def query_service_instances(duration, service_id):
    query = """
    query queryServiceInstance($duration: Duration!, $serviceId: ID!) {
        instanceId: getServiceInstances(duration: $duration, serviceId: $serviceId) {
            key: id
            label: name
        }
    }
    """
    variables = {
        "duration": duration,
        "serviceId": service_id
    }
    response = requests.post(SKYWALKING_API_URL, json={"query": query, "variables": variables})
    return response.json().get('data', {}).get('instanceId', [])

# 查询追踪的函数
def query_traces(trace_condition):
    query = """
    query queryTraces($condition: TraceQueryCondition) {
        data: queryBasicTraces(condition: $condition) {
            traces {
                key: segmentId
                endpointNames
                duration
                start
                isError
                traceIds
            }
            total
        }
    }
    """
    response = requests.post(SKYWALKING_API_URL, json={"query": query, "variables": trace_condition})
    return response.json().get('data', {}).get('queryBasicTraces', {}).get('traces', [])

# 查询追踪的辅助函数，适用于多进程调用
def fetch_traces(service_data):
    service_id, instances, current_time = service_data

    results = []
    
    # 循环遍历每个实例并查询追踪
    for instance in instances:
        trace_condition = {
            "queryDuration": {
                "start": current_time.strftime("%Y-%m-%d %H%M"),
                "end": (current_time + timedelta(minutes=1)).strftime("%Y-%m-%d %H%M"),
                "step": "MINUTE"
            },
            "traceState": "ALL",
            "paging": {
                "pageNum": 1,
                "pageSize": 15,
                "needTotal": True
            },
            "queryOrder": "BY_START_TIME",
            "serviceId": service_id
        }

        traces = query_traces(trace_condition)

        for trace in traces:
            results.append({
                "service_key": service_id,
                "instance_key": instance['key'],
                "instance_label": instance['label'],
                "segment_id": trace['key'],
                "endpoint_names": trace['endpointNames'],
                "duration": trace['duration'],
                "start": trace['start'],
                "is_error": trace['isError'],
                "trace_ids": trace['traceIds']
            })
    
    return results

# 主函数
def main():
    # 定义查询参数
    duration = {
        "start": "2024-09-28 00",
        "end": "2024-09-29 23",
        "step": "HOUR"
    }
    
    keyword = ""
    
    # 定义时间范围（可以根据需要调整）
    start_time = datetime(2024, 9, 28, 0, 0)  # 开始时间设为当天的0点
    end_time = datetime(2024, 9, 28, 23, 59)   # 结束时间设为当天的23点59分
    
    # 查询服务
    services = query_services(duration, keyword)
    
    results = []

    # 遍历每个服务并查询实例
    with ProcessPoolExecutor() as executor:
        future_to_service_data = {}
        
        for service in services:
            service_id = service['key']
            
            # 查询该服务的实例
            instances = query_service_instances(duration, service_id)
            
            current_time = start_time
            
            while current_time <= end_time:
                future_to_service_data[executor.submit(fetch_traces, (service_id, instances, current_time))] = (service['label'], current_time)
                
                # 进入下一分钟
                current_time += timedelta(minutes=1)

        # 收集结果
        for future in as_completed(future_to_service_data):
            service_label, current_time = future_to_service_data[future]
            try:
                result_data = future.result()
                results.extend(result_data)
            except Exception as exc:
                print(f"{service_label} at {current_time} generated an exception: {exc}")

    # 保存结果为 Excel 文件
    df = pd.DataFrame(results)
    df.to_excel("skywalking_traces.xlsx", index=False)

if __name__ == "__main__":
    main()