## `LifToTif.sh` 完整内容

```bash

#SBATCH -J bioimage_process     # 指定进程名称
#SBATCH -o logs/job.%j.out      # outlog 输出位置（%j 表示作业号）
#SBATCH -e logs/job.%j.err      # errlog 输出位置
#SBATCH -p C64M512G             # 选择使用的 CPU
#SBATCH --qos=normal            # 任务优先级（默认 normal）
#SBATCH --nodes=1               # 申请节点数为 1, 如果作业不能跨节点 (MPI) 运行, 申请的节点数应不超过 1;
#SBATCH --ntasks-per-node=1     # 每个节点上运行一个任务，默认情况下也可理解为每个节点使用一个核心
#SBATCH --cpus-per-task=4       # 每个任务所需要的核心数
#SBATCH --time=12:00:00         # 允许作业运行的最大时间         


# 创建日志目录
mkdir -p logs

source activate test

SCRIPT_PATH="/gpfs/share/home/2301920002/test/test_auto.py"         # 替换为实际 test_auto.py 脚本路径
INPUT_FILE="/gpfs/share/home/2301920002/20250310-plateS11-10celllines-seqF1.lif"          # 替换为实际输入文件路径
OUTPUT_DIR="/gpfs/share/home/2301920002/test/round11/"              # 替换为实际输出目录
PREFIX=""         # 替换为实际前缀

mkdir -p "${OUTPUT_DIR}"

python "${SCRIPT_PATH}" "${INPUT_FILE}" "${OUTPUT_DIR}" "${PREFIX}"

```




##########################################################################################################


## decon.sh完整内容

```bash

#!/bin/bash
#SBATCH -o logs/decon_gpu.%j.out   
#SBATCH -e logs/decon_gpu.%j.err   
#SBATCH -p GPUA800                # 选择使用的 GPU
#SBATCH -J Decon_GPU              
#SBATCH --nodes=1                 
#SBATCH --ntasks-per-node=1        
#SBATCH --cpus-per-task=8          
#SBATCH --gres=gpu:1              # 每个作业调用的 GPU 数   
#SBATCH --mem=64G                 
#SBATCH --time=72:00:00            
#SBATCH --array=1-320%4          # `SBATCH --array=1-n%m`，`n` 为最大作业数，`m` 为并行作业数 （也可指定处理部分作业，如SBATCH --array=100-200%4）
                                 # 若作业数超过 1000，可创建`filelist01.txt` `filelist02.txt` 等分别存储，分次提交；或先运行filelist.txt前 1000 个作业，完成后删除，再修改 `n`， 然后运行剩余作业。

### 2. 文件路径配置 ###
INPUT_DIR="/gpfs/share/home/2301920002/test/round11/"   # input 的路径是文件存放的第一级目录
OUTPUT_DIR="/gpfs/share/home/2301920002/storage/data/round/" # 输出目录（替换为实际路径）
TEMP_DIR="/gpfs/share/home/2301920002/WORK/temp"     # 临时文件存储位置（替换为实际路径）
FILELIST="filelist.txt"             # 这里需要确保 `filelist.txt` 和 `decon.sh` 在同一目录下

### 3. Python 脚本配置 ###
PYTHON_SCRIPT="/gpfs/share/home/2301920002/WORK/decon-sparse_block/decon_mod.py"    # 处理脚本路径
CONFIG_FILE="/gpfs/share/home/2301920002/WORK/decon-sparse_block/config_level2.ini" # 配置文件路径

source activate decon1

# 创建日志目录
mkdir -p logs

# 激活环境前记录初始化时间
init_time=$(date '+%Y-%m-%d %H:%M:%S')
echo "==== JOB START ===="
echo "Slurm_JOBID: $SLURM_JOBID"
echo "Slurm_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"
echo "System start time: $init_time"



# 获取当前任务对应的文件路径
FILE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $FILELIST)

# 任务开始时间戳（写入日志头部）
task_start=$(date +%s)
echo "---- TASK START ----"
echo "Task_START_EPOCH: $task_start"
echo "Task_START_DATE: $(date -d @$task_start '+%Y-%m-%d %H:%M:%S')"
echo "Processing file: $FILE"

# 生成输出子目录路径
rel_path="${FILE#$INPUT_DIR}"
subdir=$(dirname "$rel_path")
output_subdir="${OUTPUT_DIR}${subdir}"
mkdir -p "$output_subdir"

# 创建任务专用临时目录
temp_subdir="${TEMP_DIR}/task_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$temp_subdir"

# 处理文件名
base_name=$(basename "$FILE" .tif)

# 执行Decon处理（核心耗时部分）
python_start=$(date +%s)
echo "[PYTHON] Start: $(date -d @$python_start '+%H:%M:%S')"

python $PYTHON_SCRIPT \
  -i "$FILE" \
  -o "$output_subdir" \
  -t "$temp_subdir" \
  -p "$base_name" \
  -c "$CONFIG_FILE"

python_end=$(date +%s)
python_duration=$((python_end - python_start))
echo "[PYTHON] End: $(date -d @$python_end '+%H:%M:%S') | Duration: ${python_duration}s"

# 清理临时目录（可选）
rm -rf "$temp_subdir"

# 计算并输出时间统计
task_end=$(date +%s)
total_duration=$((task_end - task_start))

echo "---- TASK COMPLETE ----"
echo "Task_END_EPOCH: $task_end"
echo "Task_END_DATE: $(date -d @$task_end '+%Y-%m-%d %H:%M:%S')"
echo "Total duration: ${total_duration} seconds"
echo "Breakdown:"
echo "  - Python processing: ${python_duration}s"
echo "  - System overhead: $((total_duration - python_duration))s"

```

#########################################################################################################


## 使用方式
- 修改 `LifToTif.sh` 和 `decon.sh` 中的hpc配置和路径配置
- sbatch LifToTif.sh        # 使用 `LifToTif.sh` 调用 `test_auto.py`把lif文件拆解为指定格式的tif文件 
- find /gpfs/share/home/2301920002/test/round11/ -type f -name "*.tif" > filelist.txt      # 前置步骤：生成 `filelist.txt`（用于对作业数组进行管理）
- sbatch decon.sh           # 使用 `decon.sh` 调用 `decon_mod.py`对tif文件进行sparsed处理
