#!/bin/bash
last_job_id=$(squeue | grep ' R ' | awk '{print $1}')
scancel "$last_job_id"
echo "The result of squeue: "
sleep 2
squeue