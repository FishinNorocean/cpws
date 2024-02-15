#!/bin/bash


ids=$(squeue | grep -E ' (R|PD) ' | awk '{print $1}')

# 使用read命令和循环将字符串分隔成数组（以换行符分隔）
IFS=$'\n' read -r -d '' -a array <<< "$ids"

# 初始化一个空字符串来存储结果
result=""

# 遍历数组并构建输出字符串
for ((i = 0; i < ${#array[@]}; i++)); do
    # 检查是否是第一个元素，如果不是，在元素前加逗号
    if [ $i -gt 0 ]; then
        result+=","  # 添加逗号
    fi
    result+="${array[i]}"  # 添加数组元素到结果字符串
done
watch -n 1 "sacct -j $result --field=jobid,jobname,nodelist,elapsed,state"
