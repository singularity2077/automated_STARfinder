# Automated Image Processing Pipeline System

## Project Overview

This is a system for automating image processing workflows, primarily used for managing and executing a series of image processing steps, including registration, stitching, and other operations. The system is based on the SLURM job scheduling system and supports parallel processing and batch task management.

## Main Features

1. Global Registration
2. Local Registration
3. Spot Finding
4. Local Stitch
5. IF Registration
6. IF2 Registration (optional)
7. IF1 Stitch
8. Point Stitch
9. IF2 Stitch (optional)

## System Requirements

- Python 3.x
- SLURM job scheduling system
- MATLAB 2023a
- ImageJ/Fiji
- Sufficient storage space and computing resources

## Directory Structure

```
.
├── main.py                 # Main program
├── generate_scripts.py     # Script generator
├── config.ini             # Configuration file
├── 01_global_registration.sh     # Global registration script
├── 02_local_registration_batch*.sh  # Local registration scripts
├── 03_spot_finding_batch*.sh    # Spot finding scripts
├── 04_local_stitch.sh     # Local stitch script
├── 05_IF_registration.sh  # IF registration script
├── 05_IF2_registration.sh # IF2 registration script (if enabled)
├── 06_IF1_stitch_*.srp    # IF1 stitch scripts
├── 07_*_IF1_stitch_*.srp  # Subsequent protein stitch scripts
├── 09_*_IF2_stitch_*.srp  # IF2 stitch scripts (if enabled)
├── 10_stitchpoint.srp     # Point stitch script
├── logs_global_registration/    # Global registration logs
├── logs_local_registration/     # Local registration logs
├── logs_spot_finding/           # Spot finding logs
├── logs_local_stitch/           # Local stitch logs
├── logs_IF_registration/        # IF registration logs
├── logs_stitchdapinew/          # DAPI stitch logs
├── logs_stitchflanew/           # Flamingo stitch logs
└── logs_stitchpoint/            # Point stitch logs
```

## Configuration File Description

The configuration file `config.ini` contains the following main sections:

- `[PROJECT]`: Basic project information
  - `project_name`: Project name
  - `project_root`: Project root directory
  - `matlab_src`: MATLAB source code path
  - `matlab_archive`: MATLAB archive path
  - `core_matlab_dir`: Core MATLAB code directory

- `[GLOBAL_REGISTRATION]`: Global registration parameters
  - `gr_array_tasks`: Number of tasks
  - `gr_parallel_tasks`: Number of parallel tasks

- `[LOCAL_REGISTRATION]`: Local registration parameters
  - `lr_array_tasks`: Number of tasks
  - `lr_parallel_tasks`: Number of parallel tasks
  - `spotfinding_method`: Spot finding method
  - `sqrt_pieces`: Number of sub-image blocks
  - `voxel_size`: Voxel size
  - `end_bases`: Number of end bases
  - `barcode_mode`: Barcode mode
  - `split_loc`: Split location
  - `intensity_threshold`: Intensity threshold

- `[LOCAL_STITCH]`: Local stitch parameters
  - `ls_array_tasks`: Number of tasks
  - `ls_parallel_tasks`: Number of parallel tasks

- `[IF_REGISTRATION]`: IF registration parameters
  - `ir_array_tasks`: Number of tasks
  - `ir_parallel_tasks`: Number of parallel tasks

- `[IF2_REGISTRATION]`: IF2 registration parameters (optional)
  - `if2_enabled`: Whether IF2 is enabled
  - `ir2_array_tasks`: Number of tasks
  - `ir2_parallel_tasks`: Number of parallel tasks

- `[IF1_GLOBAL_STITCH]`: IF1 stitch parameters
  - `proteins`: Protein list
  - `imagej_path`: ImageJ path
  - `grid_type`: Grid type
  - `grid_order`: Grid order
  - `grid_size_x`: Grid X size
  - `grid_size_y`: Grid Y size
  - `tile_overlap`: Tile overlap

- `[IF2_GLOBAL_STITCH]`: IF2 stitch parameters (optional)
  - `if2_enabled`: Whether IF2 is enabled
  - `proteins`: Protein list
  - `imagej_path`: ImageJ path

## Usage

1. Configure the `config.ini` file with relevant parameters
2. Submit the main program:
   ```bash
   sbatch run_main.sh --startfrom 03 (optional) --endwith 05 (optional) --config my_config.ini (optional)
   ```

Note: The main program will automatically call `generate_scripts.py` to generate the required scripts, so manual execution is not necessary. Scripts are regenerated each time the main program runs to ensure synchronization with the configuration file.
(You can also manually submit `generate_scripts.py` to generate processing scripts:
   ```bash
   python generate_scripts.py
   ```
  )

### Optional Parameters for `main.py` (can be added when submitting `run_main.sh`)

- `--config`: Specify the configuration file path (default: config.ini)
- `--startfrom`: Set the starting point of the workflow (optional values: 01-10, default: 01)
- `--endwith`: Set the ending point of the workflow (optional values: 01-10, default: 10)

Note:
- The value of `endwith` must be greater than or equal to the value of `startfrom`
- If the specified step does not exist, execution will proceed to the last available step
- All step numbers must correspond to the steps in the configuration file
- The step specified by the `endwith` parameter will be included in the execution range

## Processing Workflow

1. `01_global_registration.sh`: Global registration
2. `02_local_registration_batch*.sh`: Local registration (batched)
3. `03_spot_finding_batch*.sh`: Spot finding (batched)
4. `04_local_stitch.sh`: Local stitch
5. `05_IF_registration.sh`: IF registration
6. `05_IF2_registration.sh`: IF2 registration (if enabled)
7. `06_IF1_stitch_*.srp`: IF1 stitch
8. `07_*_IF1_stitch_*.srp`: Subsequent protein stitch
9. `09_*_IF2_stitch_*.srp`: IF2 stitch (if enabled)
10. `10_stitchpoint.srp`: Point stitch

## Important Notes

1. All scripts must be submitted and executed through SLURM
2. Ensure sufficient storage space and computing resources
3. Paths in the configuration file must use absolute paths
4. The processing will generate a large number of temporary files, so ensure sufficient disk space
5. It is recommended to regularly clean up log files

## Error Handling

- If script execution fails, please check the corresponding log files
- Common errors include:
  - Path does not exist
  - Insufficient permissions
  - Insufficient resources
  - Configuration file format errors

## Maintenance and Updates

- Regularly check log files
- Monitor system resource usage
- Clean up temporary files promptly
- Keep configuration files updated
