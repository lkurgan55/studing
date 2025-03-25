import time
import random
import logging
from fastapi import FastAPI
from redis.cluster import RedisCluster, ClusterNode

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# З'єднання з Redis кластером
startup_nodes = [
    ClusterNode("redis-node-1", 7000),
    ClusterNode("redis-node-2", 7001),
    ClusterNode("redis-node-3", 7002),
    ClusterNode("redis-node-4", 7003),
]

# RedisCluster автоматично знаходить всі вузли
redis_driver = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

@app.get("/test_redis")
async def test_redis():
    updated_keys = []

    for i in range(60):
        time.sleep(1)
        key = f"key:{random.randint(1, 10000)}"

        if i % 3 == 0:
            value = f"test_{i}"
            redis_driver.set(key, value)
            logging.info(f"[{i}] Write {key} = {value}")
            updated_keys.append(key)

        if i % 12 == 0 and updated_keys:
            key_to_update = random.choice(updated_keys)
            new_value = f"updated_{random.randint(10000, 20000)}"
            redis_driver.set(key_to_update, new_value)
            logging.info(f"[{i}] Update {key_to_update} = {new_value}")

    return "60 seconds done. Keys written and updated."

@app.get("/cluster_slots")
async def get_cluster_slots():
    raw = redis_driver.cluster_slots()
    result = []

    for slot_range, data in raw.items():
        start_slot, end_slot = slot_range
        master = data.get("primary")
        replicas = data.get("replicas", [])

        result.append({
            "start_slot": start_slot,
            "end_slot": end_slot,
            "master": f"{master[0]}:{master[1]}",
            "replicas": [f"{r[0]}:{r[1]}" for r in replicas]
        })

    return result
