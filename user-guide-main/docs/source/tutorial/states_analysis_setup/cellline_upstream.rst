Cell Line Upstream Analysis
===========================

The upstream analysis for cell lines is located in the ``cellline_upstream`` folder. It includes the following steps: registration, spotfinding, decoding, segmentation, stitching, assignment.

Key Resources
-------------
*   **genes.csv**: This file contains the target gene tri-barcode information.
*   **STATE-matlab-cellline**: This directory houses the core MATLAB script ``core_matlab.m`` and related MATLAB functions.

Step-by-Step Process
--------------------

01_registration_spotfinding
~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   Perform global registration across all amplification rounds.
*   Split and conduct local registration.
*   Stitch back together.
*   Register the staining rounds accordingly.

02_IF_mask
~~~~~~~~~~
*   Use Cellpose to perform 2D segmentation on DAPI and Flamingo staining.
*   Obtain a 3D mask by element-wise multiplication of the mask and the original image.

03_IF_point_stitch
~~~~~~~~~~~~~~~~~~
*   Stitch all FOVs for DAPI.
*   Apply the stitched transformation to other stainings and amplification rounds.

04_assign
~~~~~~~~~
*   Assign amplification spots to the 3D mask.
*   Generate the final output.

.. note::
   For more details, refer to the specific subdirectories and corresponding scripts in the ``cellline_upstream`` folder.