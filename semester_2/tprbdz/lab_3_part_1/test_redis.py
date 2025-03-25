import time
import redis
from datetime import datetime

SENTINELS = [("localhost", 26379), ("localhost", 26380), ("localhost", 26381)]
MASTER_NAME = "mymaster"

def get_current_master(sentinel):
    try:
        master_info = sentinel.discover_master(MASTER_NAME)
        return master_info
    except Exception:
        return None

sentinel = redis.sentinel.Sentinel(SENTINELS, socket_timeout=0.5)
current_master = get_current_master(sentinel)
print(f"Початковий master: {current_master}")

down_time = None
new_master_time = None

while True:
    master = get_current_master(sentinel)

    if master is None:
        if not down_time:
            down_time = datetime.now()
            print(f"Master недоступний: {down_time}")
    elif down_time:
        if master != current_master:
            new_master_time = datetime.now()
            print(f"Новий master: {master} обраний о {new_master_time}")
            delta = new_master_time - down_time
            print(f"Тривалість делегування: {delta.total_seconds():.3f} секунд")
            break

    time.sleep(1)
