#!/bin/bash
running_job_id=$(squeue | grep ' R ' | awk '{print $1}')
if [ -z "$running_job_id" ]; then
    echo "No working jobs."
else
    watch -n 1 "sacct -u zju0018053 -j \"$running_job_id\" --field=jobid,jobname,nodelist,elapsed,state; tail -n 20 gpu_status.log; echo \"main.log:\"; cat results/main.log; echo \"Error:\";cat results/Error.txt"
fi
