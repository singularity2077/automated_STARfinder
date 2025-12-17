Script Interfaces
=================

This section describes the key scripts and their command-line interfaces for the Image Processing Automation System.

`main.py`
---------
The main orchestrator script for the pipeline. It reads the ``config.ini``, generates step-specific scripts using ``generate_scripts.py``, and submits them to SLURM.

**Command-Line Arguments:**

*   ``--config <path_to_config_ini>``
    *   Optional.
    *   Specifies the path to the configuration file.
    *   Default: ``config.ini`` in the current working directory.

*   ``--startfrom <step_number>``
    *   Optional.
    *   Sets the starting step of the processing workflow.
    *   Valid values: ``01`` through ``10`` (or highest step number defined).
    *   Default: ``01`` (Global Registration).

*   ``--endwith <step_number>``
    *   Optional.
    *   Sets the final step of the processing workflow (inclusive).
    *   Valid values: ``01`` through ``10``. Must be greater than or equal to ``--startfrom``.
    *   Default: ``10`` (Point Stitch) or the last available step.
    *   If a specified step does not exist (e.g., IF2 disabled), the pipeline will execute up to the last valid step before it or skip to the next valid step.

**Usage Example (typically via `run_main.sh` for SLURM):**

.. code-block:: bash

   # Assuming run_main.sh wraps the python call and handles sbatch submission
   sbatch run_main.sh --startfrom 03 --endwith 05 --config my_experiment_config.ini

`generate_scripts.py`
---------------------
This script is responsible for generating the individual shell scripts (``.sh``) and ImageJ/Fiji macro scripts (``.srp``) based on the parameters defined in ``config.ini``. It is typically called automatically by ``main.py`` but can be run manually for debugging or pre-generation.

**Command-Line Arguments:**

*   ``--config <path_to_config_ini>``
    *   Optional.
    *   Specifies the path to the configuration file.
    *   Default: ``config.ini`` in the current working directory.

**Usage Example:**

.. code-block:: bash

   python generate_scripts.py --config my_experiment_config.ini

Generated Scripts
-----------------
The following scripts are generated and used by the pipeline. They are designed to be submitted as SLURM jobs.

*   ``01_global_registration.sh``: Performs global registration.
*   ``02_local_registration_batch*.sh``: Performs local registration in batches. The ``*`` indicates multiple batch files may be generated.
*   ``03_spot_finding_batch*.sh``: Performs spot finding in batches.
*   ``04_local_stitch.sh``: Stitches locally registered image pieces.
*   ``05_IF_registration.sh``: Performs registration for primary immunofluorescence channels.
*   ``05_IF2_registration.sh``: (Optional) Performs registration for secondary immunofluorescence channels.
*   ``06_IF1_stitch_*.srp``: ImageJ/Fiji macro for stitching a specific IF1 protein/channel (e.g., ``06_IF1_stitch_DAPI.srp``). Multiple such scripts are generated based on the ``proteins`` list in ``config.ini``.
*   ``07_*_IF1_stitch_*.srp``: (Naming convention may vary) Subsequent protein stitching scripts for IF1. The exact numbering and naming depend on the implementation in ``generate_scripts.py``.
*   ``09_*_IF2_stitch_*.srp``: (Optional, naming convention may vary) ImageJ/Fiji macros for stitching IF2 proteins/channels.
*   ``10_stitchpoint.srp``: ImageJ/Fiji macro for stitching decoded points or spot data.

Each ``.sh`` script typically contains SLURM directives (``#SBATCH``) and the commands to execute the respective processing step, often involving calls to MATLAB or other tools. Each ``.srp`` file is an ImageJ/Fiji macro script.