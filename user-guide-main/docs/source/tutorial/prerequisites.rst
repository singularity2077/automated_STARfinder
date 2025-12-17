Prerequisites
=============

To effectively use the systems described in this guide, ensure the following prerequisites are met:

STATES Analysis
---------------
*   **MATLAB**: A compatible version of MATLAB is required for the core processing scripts (e.g., ``core_matlab.m``).
*   **Cellpose** (or similar segmentation tool): For image segmentation steps like ``02_IF_mask``.
*   **Sufficient Storage and Compute Resources**: STATES analysis can be data-intensive.

Image Processing Automation System
----------------------------------
*   **Python 3.x**: The main control scripts (``main.py``, ``generate_scripts.py``) are written in Python.
*   **SLURM Job Scheduling System**: The system is designed to submit jobs to SLURM.
*   **MATLAB 2023a** (or as specified in your setup): Required for MATLAB-based processing steps orchestrated by the system.
*   **ImageJ/Fiji**: Utilized for certain stitching operations.
*   **Sufficient Storage and Compute Resources**: Batch image processing requires significant disk space and computational power.