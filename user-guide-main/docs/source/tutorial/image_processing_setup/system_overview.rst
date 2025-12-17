System Overview
===============

The Image Processing Automation System is designed to automate complex image processing workflows.

Main Features
-------------
1.  **Global Registration**
2.  **Local Registration**
3.  **Spot Finding**
4.  **Local Stitch**
5.  **IF Registration**
6.  **IF2 Registration** (Optional)
7.  **IF1 Stitch**
8.  **Point Stitch**
9.  **IF2 Stitch** (Optional)

Directory Structure
-------------------
The system utilizes a specific directory structure:

.. code-block:: text

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
    ├── 06_IF1_stitch_*.srp    # IF1 stitch script
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