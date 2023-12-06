#!/bin/bash
running_job_id=$(squeue | grep -E ' (R|PD) ' | awk '{print $1}')
if [ -z "$running_job_id" ]; then
    echo "No working jobs."
    source id.sh
    watch -n 1 "sacct -j $last_job_id --field=jobid,jobname,nodelist,elapsed,state; tail -n 30 gpu_status.log; echo \"tail acu_main.log:\"; tail acu_main.log; echo \"Out & Error:\";cat Out.txt Error.txt"
else
    IFS=$'\n' read -r -d '' -a array <<< "$running_job_id"
    result=""
    for ((i = 0; i < ${#array[@]}; i++)); do
        if [ $i -gt 0 ]; then
            result+=","  # 添加逗号
        fi
        result+="${array[i]}"  # 添加数组元素到结果字符串
    done
    watch -n 1 "sacct -j $result --field=jobid,jobname,nodelist,elapsed,state; tail -n 30 gpu_status.log; echo \"tail acu_main.log:\"; tail acu_main.log; echo \"Out & Error:\";cat Out.txt Error.txt"
fi
