Image Processing Automation Example
===================================

*(This is a placeholder for a detailed walkthrough of using the Image Processing Automation System for a sample dataset. You should describe:)*
*   *(A specific imaging scenario (e.g., 3x3 tile scan with 2 fluorescent channels).)*
*   *(How to fill out ``config.ini`` for this scenario.)*
*   *(The command to submit ``main.py`` via ``run_main.sh``.)*
*   *(Expected output at various stages (e.g., after local registration, after stitching).)*
*   *(How to check logs for this example.)*

Example Scenario: Processing a Tiled Microscopy Experiment
----------------------------------------------------------
Suppose we have a 2x2 tiled dataset with DAPI and one protein channel (e.g., Flamingo) that needs to be registered and stitched. We will use Global Registration, Local Registration, IF Registration, and then stitch DAPI and Flamingo.

1.  **`config.ini` Setup**:

    .. code-block:: ini

       [PROJECT]
       project_name = MyTiledExperiment
       project_root = /data/my_user/tiled_experiment
       matlab_src = /opt/shared_matlab_scripts/image_processing_suite
       matlab_archive = /opt/MATLAB/R2023a
       core_matlab_dir = core_processing_v1

       [GLOBAL_REGISTRATION]
       gr_array_tasks = 4
       gr_parallel_tasks = 2
       # ... other relevant GR params

       [LOCAL_REGISTRATION]
       lr_array_tasks = 4
       lr_parallel_tasks = 4
       spotfinding_method = 2
       sqrt_pieces = 1
       # ... other relevant LR params

       [IF_REGISTRATION]
       ir_array_tasks = 4
       ir_parallel_tasks = 4
       # ... other relevant IR params

       [IF1_GLOBAL_STITCH]
       proteins = DAPI, Flamingo
       imagej_path = /opt/Fiji.app/ImageJ-linux64
       grid_type = Row-by-row
       grid_order = Right & Down
       grid_size_x = 2
       grid_size_y = 2
       tile_overlap = 15 # in percent
       # ... other relevant Stitch params

       # Ensure IF2 sections are disabled if not used
       [IF2_REGISTRATION]
       if2_enabled = false

       [IF2_GLOBAL_STITCH]
       if2_enabled = false

2.  **Running the Pipeline**:
    Submit the job to SLURM, perhaps starting from global registration and ending after IF1 stitching (step 07 for DAPI, step 08 for Flamingo, assuming these are how your script numbers them for proteins).

    .. code-block:: bash

       sbatch run_main.sh --config /data/my_user/tiled_experiment/config.ini --startfrom 01 --endwith 08 # Adjust endwith based on actual script numbering

3.  **Expected Outputs**:
    *   After `01_global_registration`: Transformation matrices.
    *   After `02_local_registration`: Locally registered image chunks.
    *   ...
    *   After `06_IF1_stitch_DAPI.srp` (or similar): Stitched DAPI image.
    *   After `07_IF1_stitch_Flamingo.srp` (or similar): Stitched Flamingo image.

4.  **Checking Logs**:
    Monitor `logs_global_registration/`, `logs_local_registration/`, `logs_stitchdapinew/`, etc., for progress and errors.