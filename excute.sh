#!/bin/bash
echo "Initializing"
directory="./results"  
if [ ! -d "$directory" ]; then
    echo "./results directory isn't here. Setting it up..."
    mkdir -p "$directory" 
    echo "Done"
else
    echo "./results directory already exists"
fi
log_d = "./log"
if [ ! -d "$log_d" ]; then
    echo "./log log isn't here. Setting it up..."
    mkdir -p "$directory" 
    echo "Done"
else
    echo "./log directory already exists"
fi

sbatch run.sh &

watch -n 1 "squeue; cat gpu_status.log"
