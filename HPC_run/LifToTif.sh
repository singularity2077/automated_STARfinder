#!/bin/bash
#SBATCH -J bioimage_process         
#SBATCH -o logs/job.%j.out           
#SBATCH -e logs/job.%j.err           
#SBATCH -p C64M512G
#SBATCH --qos=normal                 
#SBATCH --nodes=1                    
#SBATCH --ntasks-per-node=1          
#SBATCH --cpus-per-task=4            
#SBATCH --mem=128G                
#SBATCH --time=12:00:00             


# 创建日志目录
mkdir -p logs

source activate test

SCRIPT_PATH="/gpfs/share/home/2301920002/test/test_auto.py" # 替换为实际脚本路径
INPUT_FILE="/gpfs/share/home/2301920002/20250310-plateS11-10celllines-seqF1.lif"          # 替换为输入文件路径
OUTPUT_DIR="/gpfs/share/home/2301920002/test/round11/"              # 替换为输出目录
PREFIX=""          # 替换为实际前缀

mkdir -p "${OUTPUT_DIR}"

python "${SCRIPT_PATH}" "${INPUT_FILE}" "${OUTPUT_DIR}" "${PREFIX}"
