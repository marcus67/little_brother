#!/usr/bin/env bash
echo "Starting Little-Brother in Slave Mode"
run_little_brother.py \
     --config /etc/little-brother.config \
     --option MasterConnector.host_url=${MASTER_HOST_URL} \
              MasterConnector.access_token=${MASTER_ACCESS_TOKEN}
