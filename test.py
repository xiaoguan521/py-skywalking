from datetime import datetime

# 时间戳（毫秒）
timestamp_ms = 1727620913349

# 转换为秒
timestamp_s = timestamp_ms / 1000.0

# 转换为可读格式
readable_time = datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')

print(readable_time)
