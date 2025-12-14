print("Starting Grid/Collection stitching...");

run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down] grid_size_x=1 grid_size_y=1 tile_overlap=10 first_file_index_i=1 directory=\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein1/ file_names=Position{iii}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

print("Finished Grid/Collection stitching.");

saveAs("Tiff", "\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein1/protein1big3dnew.tif");

run("Z Project...", "projection=[Max Intensity]");
saveAs("Tiff", "\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein1/protein1big2dnew.tif");

close();
close();
