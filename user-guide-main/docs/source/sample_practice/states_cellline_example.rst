STATES Cell Line Analysis Example
=================================

*(This is a placeholder for a detailed walkthrough of a sample cell line dataset analysis using the STATES pipeline. You should describe:)*
*   *(Input data preparation (e.g., raw image files, ``genes.csv`` setup).)*
*   *(Key parameter settings for each step (01_registration_spotfinding, 02_IF_mask, etc.).)*
*   *(Expected intermediate and final outputs.)*
*   *(Common troubleshooting tips for this specific example.)*

Example Scenario
----------------
Let's assume we have a small dataset from a 2-round amplification experiment on a specific cell line.

1.  **Data Organization**:
    *   Raw TIFF files from microscope organized by round and field of view.
    *   `genes.csv` prepared with barcodes for target genes.

2.  **Running Step 01 (Registration & Spotfinding)**:
    *   Configure relevant parameters for `core_matlab.m`.
    *   Execute the MATLAB scripts for this step.
    *   Verify output: registered images, initial spot lists.

3.  **Running Step 02 (IF Mask Generation)**:
    *   Input: DAPI and Flamingo stained images.
    *   Run Cellpose for segmentation.
    *   Execute MATLAB script for mask generation.
    *   Verify output: 3D cell masks.

*(Continue for other relevant steps in your example.)*