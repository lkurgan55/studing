#!/bin/bash

sleep 60  # або перевірка через netcat


redis-cli -p 7000 --cluster create \
  redis-node-1:7000 \
  redis-node-2:7001 \
  redis-node-3:7002 \
  --cluster-replicas 0 \
  --cluster-yes
