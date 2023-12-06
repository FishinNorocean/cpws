#!/bin/bash
> gpu_status.log
echo "Timestamp: $(date)" >> gpu_status.log
while true; do
#    echo "Timestamp: $(date)" >> gpu_status.log
    nvidia-smi >> gpu_status.log
    head -n 10 /proc/meminfo >> gpu_status.log
    sleep 5
done
