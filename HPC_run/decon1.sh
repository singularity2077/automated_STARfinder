#!/bin/bash
#SBATCH -o logs/decon_gpu.%j.out   
#SBATCH -e logs/decon_gpu.%j.err   
#SBATCH -p GPUA800                
#SBATCH -J Decon_GPU              
#SBATCH --nodes=1                 
#SBATCH --ntasks-per-node=1        
#SBATCH --cpus-per-task=8          
#SBATCH --gres=gpu:1               
#SBATCH --mem=64G                
#SBATCH --time=72:00:00            
#SBATCH --array=1-320%4

### 2. 文件路径配置 ###
INPUT_DIR="/gpfs/share/home/2301920002/test/round11/"  # 输入文件目录
OUTPUT_DIR="/gpfs/share/home/2301920002/storage/data/round/" # 输出文件目录
TEMP_DIR="/gpfs/share/home/2301920002/WORK/temp"     # 临时文件目录
FILELIST="filelist.txt"             # 输入文件列表文件名

### 3. Python 脚本配置 ###
PYTHON_SCRIPT="/gpfs/share/home/2301920002/WORK/decon-sparse_block/decon_mod.py" # 处理脚本路径
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
