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

sbatch run.sh &

watch -n 2 "cat gpu_status.log"
