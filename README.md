## 了解 skywalking 的相关 graphql 接口

### 通过 查看 sky walking 的在线演示地址 <https://skywalking.apache.org/> 进入对应页面

### 记录页面上的调用逻辑按照顺序依次如下

#### 1. 查询 service

请求

```query
query queryServices($duration: Duration!,$keyword: String!) {
    services: getAllServices(duration: $duration, group: $keyword) {
        key: id
        label: name
        group
    }
}
```

```GRAPHQL VARIABLES
{
    "duration": {
        "start": "2024-09-29 20",
        "end": "2024-09-29 21",
        "step": "HOUR"
        },
    "keyword": "agent"
}
```

结果

```result
{
    "data": {
        "services": [
            {
                "key": "YWdlbnQ6OnNvbmdz.1",
                "label": "agent::songs",
                "group": "agent"
            },
            {
                "key": "YWdlbnQ6OmZyb250ZW5k.1",
                "label": "agent::frontend",
                "group": "agent"
            }
        ]
    }
}
```

#### 2. 查询实例

请求

```query
 query queryServiceInstance($duration: Duration!, $serviceId: ID!) {
        instanceId: getServiceInstances(duration: $duration, serviceId: $serviceId) {
            key: id
            label: name
        }
    }
```

```GRAPHQL VARIABLES
{
    "duration": {
        "start": "2024-09-29 13",
        "end": "2024-09-29 13",
        "step": "HOUR"
        },
    "serviceId": "YWdlbnQ6OnNvbmdz.1"
}
```

结果

```result
{
    "data": {
        "instanceId": [s
            {
                "key": "YWdlbnQ6OnNvbmdz.1_N2E5Mzk3NTY1MmNiNGJiNjkwMTY0NTc5M2U5YjA3OWNAMTAuMTE2LjMuMTU=",
                "label": "7a93975652cb4bb6901645793e9b079c@10.116.3.15"
            }
        ]
    }
}
```

#### 3. 查询接口名(端点)

请求

```query
query queryEndpoints($serviceId: ID!, $keyword: String!) {
      pods: findEndpoint(serviceId: $serviceId, keyword: $keyword, limit: 20) {
        id
        value: name
        label: name
        }
}
```

```GRAPHQL VARIABLES
{
    "serviceId":"YWdlbnQ6OnNvbmdz.1",
    "duration":{
        "start":"2024-09-29 1406",
        "end":"2024-09-29 1436",
        "step":"MINUTE"},
    "keyword":""
}
```

结果

```result
{
    "data": {
        "pods": [
        {
            "id": "YWdlbnQ6OnNvbmdz.1_SGlrYXJpQ1AvQ29ubmVjdGlvbi97dmFyfQ==",
            "value": "HikariCP/Connection/{var}",
            "label": "HikariCP/Connection/{var}"
        },
        {
            "id": "YWdlbnQ6OnNvbmdz.1_QWN0aXZlTVEvUXVldWUvcXVldWUtc29uZ3MtcGluZy9Db25zdW1lcg==",
            "value": "ActiveMQ/Queue/queue-songs-ping/Consumer",
            "label": "ActiveMQ/Queue/queue-songs-ping/Consumer"
        }
        ]
    }
}
```

#### 4. 查询 trace

请求

```query
query queryTraces($condition: TraceQueryCondition) {
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
```

```GRAPHQL VARIABLES
{
    "condition":{
            "queryDuration": {
                "start": "2024-09-29 1411",
                "end": "2024-09-29 1441",
                "step": "MINUTE"
            },
            "traceState": "ALL",
            "paging": {
                "pageNum": 1,
                "pageSize": 100
            },
            "queryOrder": "BY_START_TIME",
            "serviceId": "YWdlbnQ6OnNvbmdz.1"
        }
}
```

结果

```result
{
    "data": {
        "queryBasicTraces": {
            "traces": [
                {
                    "key": "7174cb99b67c8a45",
                    "endpointNames": [
                        "UndertowDispatch"
                    ],
                    "duration": 2,
                    "start": "1727620913349",
                    "isError": false,
                    "traceIds": [
                        "d357ee92-fc12-4b03-83f4-dbf63038e448"
                    ]
                },
                {
                    "key": "6f3b67caeafdf460",
                    "endpointNames": [
                        "GET:/songs/top"
                    ],
                    "duration": 4,
                    "start": "1727620593682",
                    "isError": false,
                    "traceIds": [
                        "20a148da-ac29-4797-a325-175cb0ff5857"
                    ]
                }
            ]
        }
    }
}
```

## 上面的接口 官方地址

https://skywalking.apache.org/docs/main/latest/en/api/query-protocol/
https://github.com/apache/skywalking-query-protocol

## 说明

本次只是想统计 🔝 时间内的接口调用次数和 执行时间,所以 把 1 和 4 接口组合就可以遍历全量数据了,参考 sky walking2.py
