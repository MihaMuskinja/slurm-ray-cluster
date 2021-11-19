#!/bin/bash

################# DON NOT CHANGE THINGS HERE UNLESS YOU KNOW WHAT YOU ARE DOING ###############
# This script is a modification to the implementation suggest by gregSchwartz18 here:
# https://github.com/ray-project/ray/issues/826#issuecomment-522116599
redis_password=$(uuidgen)
export redis_password

nodes=$(scontrol show hostnames $SLURM_JOB_NODELIST) # Getting the node names
nodes_array=( $nodes )

node_1=${nodes_array[0]} 
ip=$(srun --nodes=1 --ntasks=1 -w $node_1 hostname --ip-address) # making redis-address
port=6379
ip_head=$ip:$port
export ip_head
echo "IP Head: $ip_head"

export NUM_CPU=32
echo "Running with ${NUM_CPU} on each node"

echo "STARTING HEAD at $node_1"
srun --nodes=1 --ntasks=1 --cpus-per-task=$NUM_CPU -w $node_1 start-head.sh $ip $redis_password $NUM_CPU &
sleep 60

worker_num=$(($SLURM_JOB_NUM_NODES - 1)) #number of nodes other than the head node
for ((  i=1; i<=$worker_num; i++ ))
do
  node_i=${nodes_array[$i]}
  echo "STARTING WORKER $i at $node_i"
  srun --nodes=1 --ntasks=1 --cpus-per-task=$NUM_CPU -w $node_i start-worker.sh $ip_head $redis_password $NUM_CPU &
  sleep 5
done
##############################################################################################

#### call your code below
python examples/test_cluster.py
exit
