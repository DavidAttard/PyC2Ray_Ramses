#!/bin/bash

#SBATCH -A hestiaeor
#SBATCH --job-name="src_list"
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=0
#SBATCH --partition=batch
#SBATCH --output=./log/%x.%j.o
#SBATCH --error=./log/%x.%j.e
#SBATCH --mail-type=ALL
#SBATCH --mail-user=da500@sussex.ac.uk
#SBATCH --array=22-38
#======START=====
#module load defaults/GPU
module load Stages/2024
module load Python

array_task_id=$SLURM_ARRAY_TASK_ID

python produce_source_list.py "$array_task_id"
#=====END====
