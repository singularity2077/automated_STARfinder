# 图像处理流程自动化系统

## 项目概述

这是一个用于自动化图像处理流程的系统，主要用于管理和执行一系列图像处理步骤，包括配准、拼接等操作。系统基于 SLURM 作业调度系统，支持并行处理和批量任务管理。

## 主要功能

1. 全局配准（Global Registration）
2. 局部配准（Local Registration）
3. 点检测（Spot Finding）
4. 局部拼接（Local Stitch）
5. IF配准（IF Registration）
6. IF2配准（IF2 Registration，可选）
7. IF1拼接（IF1 Stitch）
8. 点拼接（Point Stitch）
9. IF2拼接（IF2 Stitch，可选）

## 系统要求

- Python 3.x
- SLURM 作业调度系统
- MATLAB 2023a
- ImageJ/Fiji
- 足够的存储空间和计算资源

## 目录结构

```
.
├── main.py                 # 主程序
├── generate_scripts.py     # 脚本生成器
├── config.ini             # 配置文件
├── 01_global_registration.sh     # 全局配准脚本
├── 02_local_registration_batch*.sh  # 局部配准脚本
├── 03_spot_finding_batch*.sh    # 点检测脚本
├── 04_local_stitch.sh     # 局部拼接脚本
├── 05_IF_registration.sh  # IF配准脚本
├── 05_IF2_registration.sh # IF2配准脚本（如果启用）
├── 06_IF1_stitch_*.srp    # IF1拼接脚本
├── 07_*_IF1_stitch_*.srp  # 后续蛋白质拼接脚本
├── 09_*_IF2_stitch_*.srp  # IF2拼接脚本（如果启用）
├── 10_stitchpoint.srp     # 点拼接脚本
├── logs_global_registration/    # 全局配准日志
├── logs_local_registration/     # 局部配准日志
├── logs_spot_finding/           # 点检测日志
├── logs_local_stitch/           # 局部拼接日志
├── logs_IF_registration/        # IF配准日志
├── logs_stitchdapinew/          # DAPI拼接日志
├── logs_stitchflanew/           # Flamingo拼接日志
└── logs_stitchpoint/            # 点拼接日志
```

## 配置文件说明

配置文件 `config.ini` 包含以下主要部分：

- `[PROJECT]`：项目基本信息
  - `project_name`：项目名称
  - `project_root`：项目根目录
  - `matlab_src`：MATLAB源代码路径
  - `matlab_archive`：MATLAB归档路径
  - `core_matlab_dir`：核心MATLAB代码目录

- `[GLOBAL_REGISTRATION]`：全局配准参数
  - `gr_array_tasks`：任务数量
  - `gr_parallel_tasks`：并行任务数

- `[LOCAL_REGISTRATION]`：局部配准参数
  - `lr_array_tasks`：任务数量
  - `lr_parallel_tasks`：并行任务数
  - `spotfinding_method`：点检测方法
  - `sqrt_pieces`：子图块数量
  - `voxel_size`：体素大小
  - `end_bases`：末端碱基数
  - `barcode_mode`：条形码模式
  - `split_loc`：分割位置
  - `intensity_threshold`：强度阈值

- `[LOCAL_STITCH]`：局部拼接参数
  - `ls_array_tasks`：任务数量
  - `ls_parallel_tasks`：并行任务数

- `[IF_REGISTRATION]`：IF配准参数
  - `ir_array_tasks`：任务数量
  - `ir_parallel_tasks`：并行任务数

- `[IF2_REGISTRATION]`：IF2配准参数（可选）
  - `if2_enabled`：是否启用IF2
  - `ir2_array_tasks`：任务数量
  - `ir2_parallel_tasks`：并行任务数

- `[IF1_GLOBAL_STITCH]`：IF1拼接参数
  - `proteins`：蛋白质列表
  - `imagej_path`：ImageJ路径
  - `grid_type`：网格类型
  - `grid_order`：网格顺序
  - `grid_size_x`：网格X大小
  - `grid_size_y`：网格Y大小
  - `tile_overlap`：瓦片重叠度

- `[IF2_GLOBAL_STITCH]`：IF2拼接参数（可选）
  - `if2_enabled`：是否启用IF2
  - `proteins`：蛋白质列表
  - `imagej_path`：ImageJ路径

## 使用方法

1. 配置 `config.ini` 文件，设置相关参数
2. 提交主程序：
   ```bash
   sbatch run_main.sh --startfrom 03 (可选) --endwith 05 (可选) --config my_config.ini (可选)
   ```

注意：主程序会自动调用 `generate_scripts.py` 生成所需的脚本，无需手动运行。每次运行主程序时都会重新生成脚本，确保脚本与配置文件同步。
(当然也可以自己提交generate_scripts.py生成处理脚本：
   ```bash
   python generate_scripts.py
   ```
  )

### `main.py`(可在提交`run_main.sh`时添加)可选参数

- `--config`：指定配置文件路径（默认：config.ini）
- `--startfrom`：设置流程起始点（可选值：01-10，默认：01）
- `--endwith`：设置流程结束点（可选值：01-10，默认：10）

注意：
- `endwith`的值必须大于或等于`startfrom`的值
- 如果指定的步骤不存在，会执行到最后一个可用步骤
- 所有步骤的编号必须与配置文件中的步骤对应
- `endwith`参数指定的步骤会被包含在执行范围内

## 处理流程

1. `01_global_registration.sh`：全局配准
2. `02_local_registration_batch*.sh`：局部配准（分批次）
3. `03_spot_finding_batch*.sh`：点检测（分批次）
4. `04_local_stitch.sh`：局部拼接
5. `05_IF_registration.sh`：IF配准
6. `05_IF2_registration.sh`：IF2配准（如果启用）
7. `06_IF1_stitch_*.srp`：IF1拼接
8. `07_*_IF1_stitch_*.srp`：后续蛋白质拼接
9. `09_*_IF2_stitch_*.srp`：IF2拼接（如果启用）
10. `10_stitchpoint.srp`：点拼接

## 注意事项

1. 所有脚本必须通过 SLURM 提交执行
2. 确保有足够的存储空间和计算资源
3. 配置文件中的路径必须使用绝对路径
4. 处理过程中会生成大量临时文件，请确保有足够的磁盘空间
5. 建议定期清理日志文件

## 错误处理

- 如果脚本执行失败，请检查相应的日志文件
- 常见错误包括：
  - 路径不存在
  - 权限不足
  - 资源不足
  - 配置文件格式错误

## 维护和更新

- 定期检查日志文件
- 监控系统资源使用情况
- 及时清理临时文件
- 保持配置文件更新
