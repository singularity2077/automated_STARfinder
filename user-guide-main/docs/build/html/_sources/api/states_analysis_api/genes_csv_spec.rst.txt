`genes.csv` File Specification
==============================

The ``genes.csv`` file is a critical input for the STATES analysis pipeline, containing information about the target genes and their corresponding barcodes.

Format
------
The file is a Comma Separated Values (CSV) file. Each row typically represents a gene, and columns define attributes like the gene name and its associated tri-barcode sequence used for identification during the decoding process.

Example Structure
-----------------
While the exact column names might vary based on the specific version of the pipeline, a common structure includes:

*   **GeneName**: The official symbol or identifier for the gene.
*   **BarcodeSequence**: The sequence of fluorescent probes (tri-barcode) used to identify this gene in the amplification rounds.

 .. code-block:: text

    # Example genes.csv content
    GeneName,BarcodeSequence
    Actb,123
    Gapdh,132
    Malat1,213
    ...
    
Purpose
-------
This file is used by the decoding scripts within the ``STATE-matlab-cellline`` (or tissue equivalent) functions to:
*   Map detected fluorescent spots back to specific gene targets.
*   Quantify gene expression based on the number of decoded spots per gene.

Ensure this file is accurate and correctly formatted before starting the analysis.