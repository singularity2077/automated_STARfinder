Complete Image Processing Pipeline Example
===========================================

This document provides a comprehensive walkthrough of the complete three-step image processing pipeline, from LIF file conversion through deconvolution to registration and stitching.

Pipeline Overview
------------------

This pipeline consists of three main sequential steps for processing biological image data:

1. **LIF File Splitting**: Split LIF format files into TIF files with predefined data structure
2. **Deconvolution Processing**: Perform deconvolution operations on TIF files to improve image quality
3. **Registration and Stitching**: Execute complete image processing workflow from registration to stitching

.. important::
   Each step must be executed sequentially. The next step can only begin after the previous step is completed.

Step 1: LIF to TIF File Conversion
-----------------------------------

Function Description
~~~~~~~~~~~~~~~~~~~~

Split LIF (Leica Image File) format files into multiple TIF files and organize the output according to a predefined data structure.

Script Location
~~~~~~~~~~~~~~~

The script is located at: ``decon-sparse_block-main/HPC_run/LifToTif.sh``

Configuration Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before running, modify the following parameters in the ``LifToTif.sh`` script:

.. code-block:: bash

   SCRIPT_PATH="/gpfs/share/home/2301920002/test/test_auto.py"  # Python processing script path
   INPUT_FILE="/gpfs/share/home/2301920002/20250310-plateS11-10celllines-seqF1.lif"  # Input LIF file path
   OUTPUT_DIR="/gpfs/share/home/2301920002/test/round11/"  # Output TIF file directory
   PREFIX=""  # File prefix (optional)

Running Commands
~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd decon-sparse_block-main/HPC_run
   sbatch LifToTif.sh

Output Results
~~~~~~~~~~~~~~

* TIF files organized according to predefined data structure are generated in the ``OUTPUT_DIR`` directory
* Log files are saved in ``logs/job.<job_id>.out`` and ``logs/job.<job_id>.err``

Checking Completion Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check job status
   squeue -u $USER

   # View output logs
   tail -f logs/job.<job_id>.out

   # Check output directory
   ls -lh <OUTPUT_DIR>

Step 2: TIF File Deconvolution Processing
------------------------------------------

Function Description
~~~~~~~~~~~~~~~~~~~~

Perform deconvolution processing on TIF files generated in Step 1 to improve image resolution and quality.

Script Location
~~~~~~~~~~~~~~~

The script is located at: ``decon-sparse_block-main/HPC_run/decon1.sh``

Configuration Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Modify Script Configuration
   Before running, modify the following parameters in the ``decon1.sh`` script:

   .. code-block:: bash

      INPUT_DIR="/gpfs/share/home/2301920002/test/round11/"  # Input file directory (output directory from Step 1)
      OUTPUT_DIR="/gpfs/share/home/2301920002/storage/data/round/"  # Output file directory
      TEMP_DIR="/gpfs/share/home/2301920002/WORK/temp"  # Temporary file directory
      FILELIST="filelist.txt"  # Input file list filename
      PYTHON_SCRIPT="/gpfs/share/home/2301920002/WORK/decon-sparse_block/decon_mod.py"  # Processing script path
      CONFIG_FILE="/gpfs/share/home/2301920002/WORK/decon-sparse_block/config_level2.ini"  # Configuration file path

2. Create File List
   .. important::
      Before running ``decon1.sh``, you must first create a ``filelist.txt`` file containing the full paths of all TIF files that need to be processed.

   Methods to create the file list:

   .. code-block:: bash

      # Method 1: Use find command to recursively find all .tif files
      cd <INPUT_DIR>
      find . -name "*.tif" -type f | sort > filelist.txt

      # Method 2: If full paths are needed
      find <INPUT_DIR> -name "*.tif" -type f | sort > filelist.txt

      # Method 3: If files are in specific subdirectories
      find <INPUT_DIR>/<subdirectory> -name "*.tif" -type f | sort > filelist.txt

      # Check file list
      wc -l filelist.txt  # Count number of files
      head -5 filelist.txt  # View first 5 lines

   .. note::
      * Each line in ``filelist.txt`` should be a complete file path
      * File paths can be relative paths (relative to script execution directory) or absolute paths
      * Ensure the paths in the file list are consistent with the ``INPUT_DIR`` configuration

3. Adjust Array Task Count
   Based on the number of files in ``filelist.txt``, modify the array task range in the script:

   .. code-block:: bash

      #SBATCH --array=1-320%4  # 1-320 means processing 320 files, %4 means running 4 tasks simultaneously

   If the number of files is N, modify it to:

   .. code-block:: bash

      #SBATCH --array=1-N%4

Running Commands
~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd decon-sparse_block-main/HPC_run

   # Ensure filelist.txt is created
   ls -lh filelist.txt

   # Submit job
   sbatch decon1.sh

Output Results
~~~~~~~~~~~~~~

* Deconvolution-processed TIF files are saved in the ``OUTPUT_DIR`` directory, maintaining the original directory structure
* Log files are saved in ``logs/decon_gpu.<job_id>.out`` and ``logs/decon_gpu.<job_id>.err``
* Each array task generates independent log files

Checking Completion Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check job status
   squeue -u $USER

   # View specific task logs
   tail -f logs/decon_gpu.<job_id>_<array_task_id>.out

   # Check output directory
   ls -lh <OUTPUT_DIR>

Step 3: Registration and Stitching Processing Pipeline
-------------------------------------------------------

Function Description
~~~~~~~~~~~~~~~~~~~~

Execute complete image processing workflow, including:

1. Global Registration
2. Local Registration
3. Spot Finding
4. Local Stitch
5. IF Registration
6. IF2 Registration (optional)
7. IF1 Stitch
8. Subsequent Protein Stitching
9. IF2 Stitching (optional)
10. Point Stitch

Script Location
~~~~~~~~~~~~~~~

The scripts are located in the ``auto_script/`` directory.

Configuration Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Configuration File Setup
   Edit the ``auto_script/config.ini`` file to configure all necessary parameters.

   Key Configuration Items:

   .. code-block:: ini

      [PROJECT]
      project_name = A1  # Project name
      project_root = /gpfs/share/home/2301920002/sample_new/Sample_re/  # Project root directory
      matlab_src = /gpfs/share/home/2301920002/TEST/starmap-matlab-sample1cluo/src/  # MATLAB source code path
      matlab_archive = /gpfs/share/home/2301920002/TEST/starmap-matlab-sample1cluo/archive/  # MATLAB archive path
      core_matlab_dir = /gpfs/share/home/2301920002/sample_new/Sample_re/sricpt/core_matlab.m  # Core MATLAB script path

      [GLOBAL_REGISTRATION]
      gr_array_tasks = 1  # Global registration task count
      gr_parallel_tasks = 1  # Parallel task count

      [LOCAL_REGISTRATION]
      lr_array_tasks = 1  # Local registration task count
      lr_parallel_tasks = 1  # Parallel task count
      # ... other parameters

      [IF1_GLOBAL_STITCH]
      proteins = protein1, protein2  # Protein list
      imagej_path = /gpfs/share/home/2301920002/Fiji.app/ImageJ-linux64  # ImageJ path
      registration_dir = /gpfs/share/home/2301920002/luocheng225_zlf_test/Sample2_HepeG2/02_registration  # Registration directory
      # ... other parameters

   .. important::
      * All paths must use **absolute paths**
      * ``project_root`` should point to the project root directory containing the ``01_data`` directory
      * ``registration_dir`` should point to the registration output directory (usually containing ``02_registration``)
      * Ensure the ``01_data`` directory contains deconvolved TIF files output from Step 2

2. Data Directory Structure
   Ensure the data directory structure is correct:

   .. code-block:: text

      <project_root>/
      ├── 01_data/          # Input data directory (contains deconvolved TIF files)
      │   ├── Position001/
      │   ├── Position002/
      │   └── ...
      ├── 02_registration/  # Registration output directory
      └── ...

Running Commands
~~~~~~~~~~~~~~~~

Basic Run (Execute Complete Pipeline)
   .. code-block:: bash

      cd auto_script
      sbatch run_main.sh

Specify Start and End Steps
   .. code-block:: bash

      # Start from step 03, end at step 05
      sbatch run_main.sh --startfrom 03 --endwith 05

      # Start from step 01, end at step 04
      sbatch run_main.sh --startfrom 01 --endwith 04

      # Use custom configuration file
      sbatch run_main.sh --config my_config.ini

Step Number Correspondence
   The step numbers correspond to the following processing stages:

   * ``01``: Global Registration
   * ``02``: Local Registration
   * ``03``: Spot Finding
   * ``04``: Local Stitch
   * ``05``: IF Registration
   * ``06``: IF1 Stitch (first protein)
   * ``07``: IF1 Stitch (subsequent proteins)
   * ``09``: IF2 Stitch (if enabled)
   * ``10``: Point Stitch

Output Results
~~~~~~~~~~~~~~

* Processed image files are saved in the ``02_registration`` directory
* Log files for each step are saved in corresponding ``logs_*`` directories:
  * ``logs_global_registration/``
  * ``logs_local_registration/``
  * ``logs_spot_finding/``
  * ``logs_local_stitch/``
  * ``logs_IF_registration/``
  * ``logs_stitch*/``

Checking Completion Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check main job status
   squeue -u $USER

   # View main program logs
   tail -f logs_main/main.<job_id>.out

   # Check logs for each step
   ls -lh logs_*/

Complete Running Example
-------------------------

The following is a complete running example showing how to execute all three steps sequentially.

Prerequisites
~~~~~~~~~~~~~

1. Ensure all necessary software environments are installed and configured:
   * Python 3.x (with required packages)
   * MATLAB 2023a
   * ImageJ/Fiji
   * SLURM job scheduling system

2. Ensure conda environments are created:
   * ``test`` environment (for LIF to TIF conversion)
   * ``decon1`` environment (for deconvolution)
   * ``Fiji`` environment (for stitching, if needed)

3. Prepare input files:
   * Original image files in LIF format

Example Configuration
~~~~~~~~~~~~~~~~~~~~~~

Assume we have the following configuration:

.. code-block:: bash

   # Project root directory
   PROJECT_ROOT="/gpfs/share/home/2301920002/my_project"

   # LIF file path
   LIF_FILE="/gpfs/share/home/2301920002/data/sample.lif"

   # Step 1 output directory
   STEP1_OUTPUT="/gpfs/share/home/2301920002/my_project/round1/"

   # Step 2 output directory
   STEP2_OUTPUT="/gpfs/share/home/2301920002/my_project/decon_output/"

   # Step 3 project root directory
   STEP3_ROOT="/gpfs/share/home/2301920002/my_project/"

Complete Running Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following commands demonstrate the complete workflow for all three steps:

Step 1: LIF to TIF File Conversion
   .. code-block:: bash

      # 1. Navigate to script directory
      cd decon-sparse_block-main/HPC_run

      # 2. Edit LifToTif.sh, modify the following parameters:
      #    - SCRIPT_PATH: Python script path
      #    - INPUT_FILE: LIF file path
      #    - OUTPUT_DIR: Output directory
      #    - PREFIX: File prefix (optional)

      # 3. Submit job
      sbatch LifToTif.sh

      # 4. Wait for job completion (can use the following command to monitor)
      watch -n 60 'squeue -u $USER'

      # 5. Check output
      ls -lh <STEP1_OUTPUT>

Step 2: TIF File Deconvolution Processing
   .. code-block:: bash

      # 1. Ensure still in decon-sparse_block-main/HPC_run directory

      # 2. Create file list
      cd <STEP1_OUTPUT>
      find . -name "*.tif" -type f | sort > ../HPC_run/filelist.txt
      cd ../HPC_run

      # 3. Check file list
      wc -l filelist.txt
      head -5 filelist.txt

      # 4. Edit decon1.sh, modify the following parameters:
      #    - INPUT_DIR: Output directory from Step 1
      #    - OUTPUT_DIR: Deconvolution output directory
      #    - TEMP_DIR: Temporary file directory
      #    - FILELIST: File list filename (usually filelist.txt)
      #    - PYTHON_SCRIPT: Python processing script path
      #    - CONFIG_FILE: Configuration file path
      #    - Array task range: Adjust --array=1-N%4 based on file count

      # 5. Submit job
      sbatch decon1.sh

      # 6. Wait for job completion
      watch -n 60 'squeue -u $USER'

      # 7. Check output
      ls -lh <STEP2_OUTPUT>

Step 3: Registration and Stitching Processing Pipeline
   .. code-block:: bash

      # 1. Navigate to auto_script directory
      cd ../../auto_script

      # 2. Edit config.ini, configure all necessary parameters:
      #    - [PROJECT] section: Project name, root directory, MATLAB paths, etc.
      #    - [GLOBAL_REGISTRATION] section: Global registration parameters
      #    - [LOCAL_REGISTRATION] section: Local registration parameters
      #    - [IF1_GLOBAL_STITCH] section: Stitching parameters
      #    - Ensure project_root points to project root directory containing 01_data directory
      #    - Ensure 01_data directory contains deconvolved TIF files output from Step 2

      # 3. Check data directory structure
      ls -lh <STEP3_ROOT>/01_data/

      # 4. Submit main program job
      sbatch run_main.sh

      # 5. Or specify start and end steps
      # sbatch run_main.sh --startfrom 01 --endwith 10

      # 6. Wait for job completion
      watch -n 60 'squeue -u $USER'

      # 7. Check output
      ls -lh <STEP3_ROOT>/02_registration/

Important Notes
---------------

General Notes
~~~~~~~~~~~~~

1. **Path Configuration**
   * All paths must use absolute paths
   * Ensure paths exist and have read/write permissions
   * Do not include special characters or spaces in paths

2. **Resource Management**
   * Ensure sufficient storage space (processing generates many temporary files)
   * Monitor memory and CPU usage
   * Adjust SLURM resource requests based on data volume

3. **Job Monitoring**
   * Regularly check job status: ``squeue -u $USER``
   * View log files to troubleshoot errors
   * Use ``scancel <job_id>`` to cancel jobs

4. **Error Handling**
   * If a step fails, check the corresponding log files
   * Common errors:
     * Path does not exist
     * Insufficient permissions
     * Insufficient resources
     * Configuration file format errors

Step-Specific Notes
~~~~~~~~~~~~~~~~~~~

Step 1 Notes
   * Ensure Python script ``test_auto.py`` exists and is executable
   * Ensure output directory has sufficient space
   * Processing time may be long for large LIF files

Step 2 Notes
   * **Must** create ``filelist.txt`` file first
   * Ensure file paths in ``filelist.txt`` are correct
   * Adjust array task range based on file count
   * GPU resources are limited, pay attention to concurrent task count (``%4`` means maximum 4 concurrent tasks)
   * Temporary directory will occupy significant space, ensure sufficient space

Step 3 Notes
   * Ensure all path configurations in ``config.ini`` are correct
   * Ensure data directory structure meets requirements
   * Ensure ``01_data`` directory contains files output from Step 2
   * If a step fails, you can use ``--startfrom`` and ``--endwith`` parameters to restart from the failed step
   * MATLAB and ImageJ paths must be correctly configured

Performance Optimization Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Parallel Processing**
   * Both Step 2 and Step 3 support parallel processing
   * Reasonably set parallel task count based on cluster resources
   * Avoid excessive parallelism causing resource competition

2. **Storage Optimization**
   * Clean up temporary files promptly
   * Use compression for infrequently used data
   * Regularly archive log files

3. **Monitoring and Debugging**
   * Use ``watch`` command to monitor job status
   * Regularly check disk usage: ``df -h``
   * Use ``htop`` or ``top`` to monitor system resources

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Job Stuck in PENDING State**
   * Check if resource requests are reasonable
   * Check if queue has resources
   * Use ``squeue -j <job_id>`` to view detailed information

2. **Job Failure**
   * View error logs: ``cat logs/*/<job_id>.err``
   * Check paths and permissions
   * Check configuration file format

3. **File Not Found**
   * Check if file path is correct
   * Check if file exists: ``ls -lh <file_path>``
   * Check relative paths and absolute paths

4. **Insufficient Memory**
   * Increase ``--mem`` parameter
   * Reduce parallel task count
   * Process data in batches

