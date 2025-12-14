print("Starting Grid/Collection stitching...");

run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory=\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein2/ layout_file=TileConfiguration.registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

print("Finished Grid/Collection stitching.");

saveAs("Tiff", "\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein2/protein2big3dnew.tif");

run("Z Project...", "projection=[Max Intensity]");
saveAs("Tiff", "\gpfs\share\home\2301920002\luocheng225_zlf_test\Sample2_HepeG2\02_registration\IF1\protein2/protein2big2dnew.tif");

close();
close();
