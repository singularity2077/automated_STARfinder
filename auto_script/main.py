#!/usr/bin/env python3
import configparser
import os
import subprocess
import sys
import time
import shutil
import argparse
from pathlib import Path
from generate_scripts import generate_scripts

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="图像处理流程主程序")
    parser.add_argument('-c', '--config', 
                        type=str, 
                        default='config.ini',
                        help='配置文件路径（默认：config.ini）')
    parser.add_argument('--startfrom',
                        type=str,
                        default='01',
                        choices=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'],
                        help='设置流程起始点（默认：01）')
    parser.add_argument('--endwith',
                        type=str,
                        default='10',
                        choices=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'],
                        help='设置流程结束点（默认：10）')
    return parser.parse_args()

def get_config_value(config, section, option, default=None):
    """获取配置值"""
    try:
        return config.get(section, option, fallback=default)
    except configparser.NoSectionError:
        return default

def load_config(config_file='config.ini'):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def submit_and_wait_job(cmd, job_name):
    """提交作业并等待完成"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"错误：提交失败\n{result.stderr}")
            return False
        
        job_id = result.stdout.strip().split()[-1]
        print(f"{job_name}作业已提交 | ID: {job_id}")
        
        # 等待作业完成
        while True:
            status = subprocess.run(f"squeue -j {job_id} -h -o '%T'",
                                  shell=True, capture_output=True, text=True)
            if not status.stdout.strip():
                print(f"{job_name} 已完成")
                break
            time.sleep(60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"提交{job_name}作业时出错：{e}")
        return False

def run_batch_jobs(config, script_prefix, section, prefix, step_name):
    """运行批处理作业"""
    array_tasks = int(config[section][f'{prefix}_array_tasks'])
    parallel_tasks = int(config[section][f'{prefix}_parallel_tasks'])
    max_per_batch = 1000
    num_batches = (array_tasks + max_per_batch - 1) // max_per_batch
    
    for batch in range(1, num_batches + 1):
        script_name = f'{script_prefix}_batch{batch}.sh'
        script_path = Path(script_name)
        
        if not script_path.exists():
            print(f"错误：脚本文件 {script_path} 不存在")
            return False
        
        offset = (batch - 1) * 1000
        current_batch_size = min(1000, array_tasks - offset)
        array_range = f"1-{current_batch_size}"
        
        cmd = (f"sbatch --array={array_range}%{parallel_tasks} "
               f"--export=ALL,OFFSET={offset} {script_name}")
        
        if not submit_and_wait_job(cmd, f"{step_name}批次 {batch}"):
            return False
    
    return True

def run_processing_pipeline(config, start_step=None, end_step=None):
    """运行处理流程"""
    # 定义处理步骤
    steps = [
        ('01_global_registration.sh', '全局配准'),
        ('02_local_registration', '局部配准'),  # 注意这里只写前缀
        ('03_spot_finding', '点检测'),  # 注意这里只写前缀
        ('04_local_stitch.sh', '局部拼接'),
        ('05_IF_registration.sh', 'IF配准')
    ]
    
    # 如果启用了IF2，添加IF2配准步骤
    if config.getboolean('IF2_REGISTRATION', 'if2_enabled', fallback=False):
        steps.append(('05_IF2_registration.sh', 'IF2配准'))
    
    # 添加拼接步骤
    proteins = config['IF1_GLOBAL_STITCH']['proteins'].split(',')
    first_protein = proteins[0].strip()
    steps.append((f'06_IF1_stitch_{first_protein}.srp', f'{first_protein}拼接'))
    
    # 添加后续蛋白质的拼接步骤
    for i, protein in enumerate(proteins[1:], 1):
        protein = protein.strip()
        steps.append((f'07_{i}_IF1_stitch_{protein}.srp', f'{protein}拼接'))
    
    # 添加点拼接步骤
    steps.append(('10_stitchpoint.srp', '点拼接'))
    
    # 如果启用了IF2拼接，添加IF2拼接步骤
    if config.getboolean('IF2_GLOBAL_STITCH', 'if2_enabled', fallback=False):
        proteins = config['IF2_GLOBAL_STITCH']['proteins'].split(',')
        for i, protein in enumerate(proteins, 1):
            protein = protein.strip()
            steps.append((f'09_{i}_IF2_stitch_{protein}.srp', f'IF2 {protein}拼接'))
    
    # 找到起始步骤的索引
    start_index = 0
    if start_step:
        for i, (step_file, _) in enumerate(steps):
            if step_file.startswith(start_step):
                start_index = i
                break
    
    # 找到结束步骤的索引
    end_index = len(steps)
    if end_step:
        for i, (step_file, _) in enumerate(steps):
            if step_file.startswith(end_step):
                end_index = i + 1
                break
    
    # 从指定步骤开始执行，到指定步骤结束
    for step_file, step_name in steps[start_index:end_index]:
        print(f"\n开始执行{step_name}...")
        
        if step_file == '02_local_registration':
            # 处理局部配准的特殊情况
            if not run_batch_jobs(config, '02_local_registration', 'LOCAL_REGISTRATION', 'lr', step_name):
                print(f"{step_name}执行失败")
                return False
            print(f"{step_name}执行完成")
        elif step_file == '03_spot_finding':
            # 处理点检测的特殊情况
            if not run_batch_jobs(config, '03_spot_finding', 'LOCAL_REGISTRATION', 'lr', step_name):
                print(f"{step_name}执行失败")
                return False
            print(f"{step_name}执行完成")
        else:
            script_path = Path(step_file)
            if not script_path.exists():
                print(f"错误：脚本文件 {script_path} 不存在")
                return False
            
            # 提交作业并等待完成
            cmd = f"sbatch --export=ALL {step_file}"
            if not submit_and_wait_job(cmd, step_name):
                return False
    
    return True

def main():
    args = parse_args()
    
    if not os.getenv('SLURM_JOB_ID'):
        sys.exit("请使用『sbatch run_main.sh』提交作业！")

    config = load_config(args.config)
    
    os.environ.update({
        'MATLAB_SRC': get_config_value(config, 'PROJECT', 'matlab_src'),
        'MATLAB_ARCHIVE': get_config_value(config, 'PROJECT', 'matlab_archive')
    })
    
    # 首先生成所有脚本
    print("\n正在生成处理脚本...")
    script_dir = generate_scripts(args.config)
    print(f"脚本已生成到目录: {script_dir}")
    
    # 运行处理流程
    if not run_processing_pipeline(config, args.startfrom, args.endwith):
        sys.exit("处理流程执行失败")

if __name__ == "__main__":
    main()
