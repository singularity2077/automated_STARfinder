Execution
=========

.. note::
   For a complete end-to-end example covering all three steps (LIF to TIF conversion, deconvolution, and registration/stitching), see :doc:`/sample_practice/complete_pipeline_example`.

Running the Pipeline
--------------------

1.  **Configure `config.ini`**: Set all relevant parameters in the ``config.ini`` file.
2.  **Submit the Main Program**:
    The primary way to run the pipeline is by submitting the ``run_main.sh`` script (not detailed in the README, but implied for SLURM submission of ``main.py``). The ``main.py`` script is typically invoked as follows:

    .. code-block:: bash

       sbatch run_main.sh --startfrom <step_number> --endwith <step_number> --config <your_config.ini>

    *   ``--startfrom <step_number>`` (Optional): Sets the starting point of the workflow (e.g., ``03`` for spot finding). Default is ``01``.
    *   ``--endwith <step_number>`` (Optional): Sets the ending point of the workflow (e.g., ``05`` for IF registration). Default is ``10``. ``endwith`` must be >= ``startfrom``.
    *   ``--config <your_config.ini>`` (Optional): Specifies a custom configuration file path. Default is ``config.ini``.

    The ``main.py`` script automatically calls ``generate_scripts.py`` to create or update the necessary shell and SRP scripts based on the current ``config.ini``. This ensures scripts are synchronized with the configuration for each run.

Alternative Script Generation
-----------------------------
You can also manually generate the processing scripts:

.. code-block:: bash

   python generate_scripts.py --config <your_config.ini>

Processing Flow
---------------
The system executes the following steps, managed by SLURM:

1.  ``01_global_registration.sh``: Global registration
2.  ``02_local_registration_batch*.sh``: Local registration (batched)
3.  ``03_spot_finding_batch*.sh``: Spot finding (batched)
4.  ``04_local_stitch.sh``: Local stitching
5.  ``05_IF_registration.sh``: IF registration
6.  ``05_IF2_registration.sh``: IF2 registration (if enabled)
7.  ``06_IF1_stitch_*.srp``: IF1 stitching (ImageJ/Fiji script)
8.  ``07_*_IF1_stitch_*.srp``: Subsequent protein stitching for IF1 (ImageJ/Fiji script)
9.  ``09_*_IF2_stitch_*.srp``: IF2 stitching (if enabled, ImageJ/Fiji script)
10. ``10_stitchpoint.srp``: Point stitching (ImageJ/Fiji script)

Important Notes
---------------
*   All scripts are designed for execution via SLURM.
*   Ensure sufficient storage space and compute resources are available.
*   Use absolute paths in ``config.ini``.
*   The process generates many temporary files; plan disk space accordingly.
*   Regularly check log files in the respective ``logs_*`` directories for monitoring and troubleshooting.

Error Handling
--------------
*   If a script fails, consult the corresponding log file in its ``logs_*`` directory.
*   Common issues include:
    *   Incorrect paths in ``config.ini``.
    *   Insufficient file permissions.
    *   Lack of compute or storage resources.
    *   Formatting errors in ``config.ini``.

Maintenance and Updates
-----------------------
*   Periodically review log files.
*   Monitor system resource usage.
*   Clean up temporary files as needed.
*   Keep the ``config.ini`` file updated with any changes to paths or parameters.