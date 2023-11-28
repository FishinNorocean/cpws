#!/bin/bash
while true; do
#    echo "Timestamp: $(date)" >> gpu_status.log
    nvidia-smi > gpu_status.log
    squeue >> gpu_status.log
    sleep 1
done
