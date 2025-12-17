`config.ini` File Reference
===========================

The ``config.ini`` file is the central configuration for the Image Processing Automation System. Below is a description of its sections and parameters. **All paths should be absolute paths.**

[PROJECT]
---------
Basic project information.

``project_name``
  Description: Name of the project.
  Type: string

``project_root``
  Description: Root directory for the project's data and outputs.
  Type: string (absolute path)

``matlab_src``
  Description: Path to the MATLAB source code directory used by the pipeline.
  Type: string (absolute path)

``matlab_archive``
  Description: Path to the MATLAB installation/archive (e.g., for runtime compilation or environment setup).
  Type: string (absolute path)

``core_matlab_dir``
  Description: Specific subdirectory within ``matlab_src`` containing core MATLAB processing scripts.
  Type: string (relative to ``matlab_src`` or absolute)

[GLOBAL_REGISTRATION]
---------------------
Parameters for the global registration step.

``gr_array_tasks``
  Description: Number of array tasks for SLURM (e.g., number of FOVs or chunks to process).
  Type: integer

``gr_parallel_tasks``
  Description: Maximum number of parallel SLURM tasks for this step.
  Type: integer

[LOCAL_REGISTRATION]
--------------------
Parameters for the local registration and spot finding step.

``lr_array_tasks``
  Description: Number of array tasks for SLURM.
  Type: integer

``lr_parallel_tasks``
  Description: Maximum number of parallel SLURM tasks.
  Type: integer

``spotfinding_method``
  Description: Method identifier for spot finding algorithm.
  Type: integer/string

``sqrt_pieces``
  Description: Number of sub-tiles per dimension to split images into for local processing (e.g., 1 for no split, 2 for 2x2 split).
  Type: integer

``voxel_size``
  Description: Voxel dimensions (e.g., "0.108,0.108,0.250" for X,Y,Z in microns).
  Type: string

``end_bases``
  Description: Number of end bases to consider for barcode design/decoding.
  Type: integer

``barcode_mode``
  Description: Mode or scheme for barcode interpretation.
  Type: string/integer

``split_loc``
  Description: Parameter related to image splitting logic.
  Type: string/integer

``intensity_threshold``
  Description: Intensity threshold for spot detection.
  Type: float/integer

[LOCAL_STITCH]
--------------
Parameters for the local stitching step.

``ls_array_tasks``
  Description: Number of array tasks for SLURM.
  Type: integer

``ls_parallel_tasks``
  Description: Maximum number of parallel SLURM tasks.
  Type: integer

[IF_REGISTRATION]
-----------------
Parameters for Immunofluorescence (IF) registration.

``ir_array_tasks``
  Description: Number of array tasks for SLURM.
  Type: integer

``ir_parallel_tasks``
  Description: Maximum number of parallel SLURM tasks.
  Type: integer

[IF2_REGISTRATION]
------------------
Parameters for secondary Immunofluorescence (IF2) registration (optional).

``if2_enabled``
  Description: Enable or disable IF2 registration.
  Type: boolean (``true`` or ``false``)

``ir2_array_tasks``
  Description: Number of array tasks for SLURM if IF2 is enabled.
  Type: integer

``ir2_parallel_tasks``
  Description: Maximum number of parallel SLURM tasks if IF2 is enabled.
  Type: integer

[IF1_GLOBAL_STITCH]
-------------------
Parameters for global stitching of primary IF channels (e.g., DAPI, Flamingo) using ImageJ/Fiji.

``proteins``
  Description: Comma-separated list of protein/channel names to stitch for IF1 (e.g., ``DAPI,Flamingo,GFP``).
  Type: string

``imagej_path``
  Description: Absolute path to the ImageJ/Fiji executable.
  Type: string (absolute path)

``grid_type``
  Description: Type of grid acquisition (e.g., ``Row-by-row``, ``Column-by-column``). Corresponds to ImageJ stitching plugin options.
  Type: string

``grid_order``
  Description: Order of tile acquisition (e.g., ``Right & Down``, ``Down & Right``). Corresponds to ImageJ stitching plugin options.
  Type: string

``grid_size_x``
  Description: Number of tiles in the X dimension.
  Type: integer

``grid_size_y``
  Description: Number of tiles in the Y dimension.
  Type: integer

``tile_overlap``
  Description: Percentage of overlap between adjacent tiles.
  Type: integer (e.g., ``15`` for 15%)

[IF2_GLOBAL_STITCH]
-------------------
Parameters for global stitching of secondary IF channels (optional).

``if2_enabled``
  Description: Enable or disable IF2 stitching.
  Type: boolean (``true`` or ``false``)

``proteins``
  Description: Comma-separated list of protein/channel names to stitch for IF2.
  Type: string

``imagej_path``
  Description: Absolute path to the ImageJ/Fiji executable (can be same as ``IF1_GLOBAL_STITCH``).
  Type: string (absolute path)

*(Note: Add any other parameters from your config.ini not explicitly mentioned in the README, like those for ``10_stitchpoint.srp`` if they are configurable via ``config.ini``)*.