#!/bin/bash
#SBATCH -o logs_main/main.%j.out
#SBATCH -e logs_main/main.%j.err
#SBATCH -J main
#SBATCH -p C64M512G
#SBATCH -c 1
#SBATCH --time=24:00:00

# 创建日志目录
mkdir -p logs_main


# 运行主程序
python main.py "$@"
