Configuration
=============

The primary configuration for the Image Processing Automation System is done via the ``config.ini`` file.

This file dictates:
*   Project paths and names.
*   Parameters for each processing step (e.g., task parallelism, image properties).
*   Paths to external tools like MATLAB and ImageJ.
*   Toggles for optional processing steps (e.g., IF2 registration/stitching).

Detailed information about each parameter in ``config.ini`` can be found in the :doc:`../../api/image_processing_api/config_ini_reference`.

Before running the system, ensure ``config.ini`` is correctly set up with absolute paths and appropriate parameters for your specific dataset and environment.