#!/bin/bash
#SBATCH -o logs_global_registration/global_registration_%A_%a.out  
#SBATCH -e logs_global_registration/global_registration_%A_%a.err
#SBATCH -J Global_Registration
#SBATCH -p C64M512G 
#SBATCH -c 8        
#SBATCH --mem=64G                  
#SBATCH --time=24:00:00
#SBATCH --array=1-1%1

module purge
module load matlab/2023a

MATLAB_SRC="/gpfs/share/home/2301920002/TEST/starmap-matlab-sample1cluo/src/"
MATLAB_ARCHIVE="/gpfs/share/home/2301920002/TEST/starmap-matlab-sample1cluo/archive/"
CORE_MATLAB_DIR="/gpfs/share/home/2301920002/sample_new/Sample_re/sricpt/core_matlab.m"
export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

PROJECT_NAME="A1"
PROJECT_ROOT="/gpfs/share/home/2301920002/sample_new/Sample_re/"
TASK_ID=$SLURM_ARRAY_TASK_ID
POSITION_NAME=$(printf "Position%03d" $TASK_ID)

matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'global_registration', '$POSITION_NAME', 2048, 32, 1, 3, 10, \
  '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'sqrt_pieces', 4)"
