Core MATLAB Functions (STATE-matlab-cellline)
=============================================

The ``STATE-matlab-cellline`` directory (and its tissue equivalent) contains the core MATLAB scripts and functions for the STATES upstream analysis. The central script is often named ``core_matlab.m`` or similar.

`core_matlab.m`
---------------
*   **Purpose**: This main script orchestrates the different stages of the upstream analysis for cell line data. It calls various sub-functions to perform specific tasks.
*   **Key Operations Invoked**:
    *   Image registration (global and local).
    *   Spot finding and quality control.
    *   Decoding of barcodes against the ``genes.csv`` file.
    *   Image segmentation (often interfacing with tools like Cellpose output).
    *   Stitching of fields of view (FOVs).
    *   Assignment of decoded spots to segmented cells/objects.
*   **Inputs**:
    *   Paths to raw image data.
    *   Path to ``genes.csv``.
    *   Configuration parameters (e.g., thresholds, channel mappings, registration settings). These might be hardcoded, passed as arguments, or read from a configuration file.
*   **Outputs**:
    *   Registered images.
    *   Spot lists with coordinates and decoded gene identities.
    *   Cell masks with assigned spots.
    *   Final expression matrices.

Related MATLAB Functions
------------------------
The ``STATE-matlab-cellline`` directory will contain numerous helper functions called by ``core_matlab.m``. These functions are specialized for tasks such as:

*   ``perform_registration.m``: Handles image alignment.
*   ``find_spots_in_round.m``: Detects fluorescent spots in a given amplification round.
*   ``decode_barcodes.m``: Matches spot sequences to gene barcodes.
*   ``segment_cells_from_IF.m``: Processes immunofluorescence images for segmentation.
*   ``stitch_fovs.m``: Combines multiple fields of view into a larger image.
*   ``assign_spots_to_cells.m``: Allocates decoded spots to cellular compartments.

*(Note: The actual names and organization of these functions may vary. This section should be updated to reflect the precise structure of your MATLAB codebase. Document key functions, their inputs, outputs, and primary purpose.)*