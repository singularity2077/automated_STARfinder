#!/usr/bin/env python3
import configparser
import os
import sys
from pathlib import Path
import subprocess
import textwrap

def generate_global_registration_script(config):
    """生成全局配准脚本"""
    script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_global_registration/global_registration_%A_%a.out  
        #SBATCH -e logs_global_registration/global_registration_%A_%a.err
        #SBATCH -J Global_Registration
        #SBATCH -p C64M512G 
        #SBATCH -c 8        
        #SBATCH --mem=64G                  
        #SBATCH --time=24:00:00
        #SBATCH --array=1-{config['GLOBAL_REGISTRATION']['gr_array_tasks']}%{config['GLOBAL_REGISTRATION']['gr_parallel_tasks']}

        module purge
        module load matlab/2023a

        MATLAB_SRC="{config['PROJECT']['matlab_src']}"
        MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
        CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
        export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

        PROJECT_NAME="{config['PROJECT']['project_name']}"
        PROJECT_ROOT="{config['PROJECT']['project_root']}"
        TASK_ID=$SLURM_ARRAY_TASK_ID
        POSITION_NAME=$(printf "Position%03d" $TASK_ID)

        matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'global_registration', '$POSITION_NAME', {config['GLOBAL_REGISTRATION']['image_width']}, {config['GLOBAL_REGISTRATION']['image_depth']}, {config['GLOBAL_REGISTRATION']['ref_round']}, {config['GLOBAL_REGISTRATION']['channel_num']}, {config['GLOBAL_REGISTRATION']['round_num']}, \\
          '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'sqrt_pieces', {config['GLOBAL_REGISTRATION']['sqrt_pieces']})"
    """)
    return script

def generate_local_registration_script(config):
    """生成局部配准脚本"""
    array_tasks = int(config['LOCAL_REGISTRATION']['lr_array_tasks'])
    parallel_tasks = int(config['LOCAL_REGISTRATION']['lr_parallel_tasks'])
    
    scripts = []
    max_per_batch = 1000
    num_batches = (array_tasks + max_per_batch - 1) // max_per_batch
    
    for batch in range(num_batches):
        offset = batch * max_per_batch
        current_batch_size = min(max_per_batch, array_tasks - offset)
        array_range = f"1-{current_batch_size}"
        
        script = textwrap.dedent(f"""\
            #!/bin/bash
            #SBATCH -o logs_local_registration/local_registration_%A_%a.out  
            #SBATCH -e logs_local_registration/local_registration_%A_%a.err
            #SBATCH -J Local_Registration
            #SBATCH -p C64M512G 
            #SBATCH -c 8        
            #SBATCH --mem=64G                  
            #SBATCH --time=24:00:00
            #SBATCH --array={array_range}%{parallel_tasks}

            module purge
            module load matlab/2023a

            MATLAB_SRC="{config['PROJECT']['matlab_src']}"
            MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
            CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
            export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

            PROJECT_NAME="{config['PROJECT']['project_name']}"
            PROJECT_ROOT="{config['PROJECT']['project_root']}"
            OFFSET=${{OFFSET:-{offset}}}  # 默认偏移为{offset}
            TASK_ID=$(( SLURM_ARRAY_TASK_ID + OFFSET ))
            SUBTILES_PER_POSITION=16  
            POSITION_INDEX=$(( (TASK_ID - 1) / SUBTILES_PER_POSITION + 1 ))
            SUBTILE_ID=$(( (TASK_ID - 1) % SUBTILES_PER_POSITION + 1 ))
            POSITION_NAME=$(printf "Position%03d" $POSITION_INDEX)

            matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'local_registration', '$POSITION_NAME', {config['LOCAL_REGISTRATION']['image_width']}, {config['LOCAL_REGISTRATION']['image_depth']}, {config['LOCAL_REGISTRATION']['ref_round']}, {config['LOCAL_REGISTRATION']['channel_num']}, {config['LOCAL_REGISTRATION']['round_num']}, \\
              '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'spotfinding_method', '{config['LOCAL_REGISTRATION']['spotfinding_method']}', 'sqrt_pieces', {config['LOCAL_REGISTRATION']['sqrt_pieces']}, \\
              'subtile', $SUBTILE_ID, 'voxel_size', {config['LOCAL_REGISTRATION']['voxel_size']}, 'end_bases', {config['LOCAL_REGISTRATION']['end_bases']}, 'barcode_mode', '{config['LOCAL_REGISTRATION']['barcode_mode']}', \\
              'split_loc', {config['LOCAL_REGISTRATION']['split_loc']}, 'intensity_threshold', {config['LOCAL_REGISTRATION']['intensity_threshold']})"
        """)
        scripts.append((f"02_local_registration_batch{batch+1}.sh", script))
    
    return scripts

def generate_local_stitch_script(config):
    """生成局部拼接脚本"""
    script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_local_stitch/local_stitch_%A_%a.out  
        #SBATCH -e logs_local_stitch/local_stitch_%A_%a.err
        #SBATCH -J Local_Stitch
        #SBATCH -p C64M512G 
        #SBATCH -c 8        
        #SBATCH --mem=64G                  
        #SBATCH --time=24:00:00
        #SBATCH --array=1-{config['LOCAL_STITCH']['ls_array_tasks']}%{config['LOCAL_STITCH']['ls_parallel_tasks']}

        module purge
        module load matlab/2023a

        MATLAB_SRC="{config['PROJECT']['matlab_src']}"
        MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
        CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
        export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

        PROJECT_NAME="{config['PROJECT']['project_name']}"
        PROJECT_ROOT="{config['PROJECT']['project_root']}"
        TASK_ID=$SLURM_ARRAY_TASK_ID
        POSITION_NAME=$(printf "Position%03d" $TASK_ID)

        matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'stitch', '$POSITION_NAME', {config['LOCAL_STITCH']['image_width']}, {config['LOCAL_STITCH']['image_depth']}, {config['LOCAL_STITCH']['ref_round']}, {config['LOCAL_STITCH']['channel_num']}, {config['LOCAL_STITCH']['round_num']}, \\
          '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'spotfinding_method', '{config['LOCAL_STITCH']['spotfinding_method']}', 'sqrt_pieces', {config['LOCAL_STITCH']['sqrt_pieces']})"
    """)
    return script

def generate_if_registration_script(config):
    """生成免疫荧光配准脚本"""
    # 从配置文件中获取蛋白标记列表
    protein_stains = config['IF_REGISTRATION']['ir_protein_stains'].strip('{}').replace("'", "").split(',')
    protein_stains_str = ", ".join(f"'{stain.strip()}'" for stain in protein_stains)
    
    script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_IF_registration/IF_registration_%A_%a.out  
        #SBATCH -e logs_IF_registration/IF_registration_%A_%a.err
        #SBATCH -J IF_Registration
        #SBATCH -p C64M512G 
        #SBATCH -c 8        
        #SBATCH --mem=64G                  
        #SBATCH --time=24:00:00
        #SBATCH --array=1-{config['IF_REGISTRATION']['ir_array_tasks']}%{config['IF_REGISTRATION']['ir_parallel_tasks']}

        module purge
        module load matlab/2023a

        MATLAB_SRC="{config['PROJECT']['matlab_src']}"
        MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
        CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
        export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

        PROJECT_NAME="{config['PROJECT']['project_name']}"
        PROJECT_ROOT="{config['PROJECT']['project_root']}"
        TASK_ID=$SLURM_ARRAY_TASK_ID
        POSITION_NAME=$(printf "Position%03d" $TASK_ID)

        matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'nuclei_protein_registration', '$POSITION_NAME', {config['IF_REGISTRATION']['ir_image_width']}, {config['IF_REGISTRATION']['ir_image_depth']}, {config['IF_REGISTRATION']['ref_round']}, {config['IF_REGISTRATION']['ir_channel_num']}, {config['IF_REGISTRATION']['ir_round_num']}, \\
          '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'protein_round', '{config['IF_REGISTRATION']['ir_if_name']}', 'protein_stains', {{{protein_stains_str}}})"
    """)
    return script

def generate_if2_registration_script(config):
    """生成IF2配准脚本"""
    # 从配置文件中获取蛋白标记列表
    protein_stains = config['IF2_REGISTRATION']['ir_protein_stains'].strip('{}').replace("'", "").split(',')
    protein_stains_str = ", ".join(f"'{stain.strip()}'" for stain in protein_stains)
    
    script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_IF_registration/IF2_registration_%A_%a.out  
        #SBATCH -e logs_IF_registration/IF2_registration_%A_%a.err
        #SBATCH -J IF2_Registration
        #SBATCH -p C64M512G 
        #SBATCH -c 8        
        #SBATCH --mem=64G                  
        #SBATCH --time=24:00:00
        #SBATCH --array=1-{config['IF2_REGISTRATION']['ir2_array_tasks']}%{config['IF2_REGISTRATION']['ir2_parallel_tasks']}

        module purge
        module load matlab/2023a

        MATLAB_SRC="{config['PROJECT']['matlab_src']}"
        MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
        CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
        export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

        PROJECT_NAME="{config['PROJECT']['project_name']}"
        PROJECT_ROOT="{config['PROJECT']['project_root']}"
        TASK_ID=$SLURM_ARRAY_TASK_ID
        POSITION_NAME=$(printf "Position%03d" $TASK_ID)

        matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'nuclei_protein_registration', '$POSITION_NAME', {config['IF2_REGISTRATION']['ir_image_width']}, {config['IF2_REGISTRATION']['ir_image_depth']}, {config['IF2_REGISTRATION']['ref_round']}, {config['IF2_REGISTRATION']['ir_channel_num']}, {config['IF2_REGISTRATION']['ir_round_num']}, \\
          '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'protein_round', '{config['IF2_REGISTRATION']['ir_if_name']}', 'protein_stains', {{{protein_stains_str}}})"
    """)
    return script

def generate_first_stitch_script(config):
    """Generate the first stitching script (script01)"""
    # 从config中获取第一个蛋白名称
    first_protein = config['IF1_GLOBAL_STITCH']['proteins'].split(',')[0].strip()
    
    # 生成文件名
    script_name = f"06_IF1_stitch_{first_protein}.srp"
    macro_name = f"06_IF1_Macro_{first_protein}.ijm"
    
    # 规范化路径
    registration_dir = os.path.normpath(config['IF1_GLOBAL_STITCH']['registration_dir'])
    protein_dir = os.path.normpath(f"{registration_dir}/IF1/{first_protein}")
    
    # 检查目录是否存在
    if not os.path.exists(protein_dir):
        print(f"警告: 目录 {protein_dir} 不存在，将自动创建")
        os.makedirs(protein_dir, exist_ok=True)
    
    # Generate .srp script
    srp_script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_stitch{first_protein}/stitch{first_protein}.%j.out
        #SBATCH -e logs_stitch{first_protein}/stitch{first_protein}.%j.err
        #SBATCH -J stitch{first_protein}
        #SBATCH -p C64M512G
        #SBATCH -c 16
        #SBATCH --time=24:00:00

        source activate Fiji
        {config['IF1_GLOBAL_STITCH']['imagej_path']} --headless --console --run "$(pwd)/{script_name.replace('.srp', '.bsh')}"
    """)
    
    # Generate .bsh script
    bsh_script = textwrap.dedent(f"""\
        // Set MPICBG parameters
        mpicbg.stitching.GlobalOptimization.ignoreZ = true;
        print("Set mpicbg.stitching.GlobalOptimization.ignoreZ = true;");

        // Import IJ
        import ij.IJ;

        // Run macro script
        String macroPath = "{macro_name}";
        print("Running macro script: " + macroPath);
        IJ.runMacroFile(macroPath);
        print("Finished running macro script.");
    """)
    
    # Generate .ijm script
    ijm_script = textwrap.dedent(f"""\
        print("Starting Grid/Collection stitching...");

        run("Grid/Collection stitching", "type=[{config['IF1_GLOBAL_STITCH']['grid_type']}] order=[{config['IF1_GLOBAL_STITCH']['grid_order']}] grid_size_x={config['IF1_GLOBAL_STITCH']['grid_size_x']} grid_size_y={config['IF1_GLOBAL_STITCH']['grid_size_y']} tile_overlap={config['IF1_GLOBAL_STITCH']['tile_overlap']} first_file_index_i=1 directory={protein_dir}/ file_names=Position{{iii}}.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

        print("Finished Grid/Collection stitching.");

        saveAs("Tiff", "{protein_dir}/{first_protein}big3dnew.tif");

        run("Z Project...", "projection=[Max Intensity]");
        saveAs("Tiff", "{protein_dir}/{first_protein}big2dnew.tif");

        close();
        close();
    """)
    
    return {
        script_name: srp_script,
        script_name.replace('.srp', '.bsh'): bsh_script,
        macro_name: ijm_script
    }

def generate_subsequent_stitch_scripts(config, protein, script_num):
    """Generate subsequent stitching scripts (script02 and later)"""
    # 从config中获取第一个蛋白名称
    first_protein = config['IF1_GLOBAL_STITCH']['proteins'].split(',')[0].strip()
    
    # 生成文件名，使用07_1_、07_2_这样的格式
    script_name = f"07_{script_num}_IF1_stitch_{protein}.srp"
    macro_name = f"07_{script_num}_IF1_Macro_{protein}.ijm"
    
    # 规范化路径
    registration_dir = os.path.normpath(config['IF1_GLOBAL_STITCH']['registration_dir'])
    first_protein_dir = os.path.normpath(f"{registration_dir}/IF1/{first_protein}")
    protein_dir = os.path.normpath(f"{registration_dir}/IF1/{protein}")
    
    # Generate .srp script
    srp_script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_stitch{protein}/stitch{protein}.%j.out
        #SBATCH -e logs_stitch{protein}/stitch{protein}.%j.err
        #SBATCH -J stitch{protein}
        #SBATCH -p C64M512G
        #SBATCH -c 16
        #SBATCH --time=24:00:00

        cp -v "{first_protein_dir}/TileConfiguration.registered.txt" "{protein_dir}/"

        source activate Fiji
        {config['IF1_GLOBAL_STITCH']['imagej_path']} --headless --console --run "$(pwd)/{script_name.replace('.srp', '.bsh')}"
    """)
    
    # Generate .bsh script
    bsh_script = textwrap.dedent(f"""\
        // Set MPICBG parameters
        mpicbg.stitching.GlobalOptimization.ignoreZ = true;
        print("Set mpicbg.stitching.GlobalOptimization.ignoreZ = true;");

        // Import IJ
        import ij.IJ;

        // Run macro script
        String macroPath = "{macro_name}";
        print("Running macro script: " + macroPath);
        IJ.runMacroFile(macroPath);
        print("Finished running macro script.");
    """)
    
    # Generate .ijm script
    ijm_script = textwrap.dedent(f"""\
        print("Starting Grid/Collection stitching...");

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory={protein_dir}/ layout_file=TileConfiguration.registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

        print("Finished Grid/Collection stitching.");

        saveAs("Tiff", "{protein_dir}/{protein}big3dnew.tif");

        run("Z Project...", "projection=[Max Intensity]");
        saveAs("Tiff", "{protein_dir}/{protein}big2dnew.tif");

        close();
        close();
    """)
    
    return {
        script_name: srp_script,
        script_name.replace('.srp', '.bsh'): bsh_script,
        macro_name: ijm_script
    }

def generate_if2_stitch_scripts(config, protein, script_num):
    """Generate IF2 stitching scripts"""
    # 从config中获取第一个蛋白名称
    first_protein = config['IF1_GLOBAL_STITCH']['proteins'].split(',')[0].strip()
    
    # 生成文件名，使用09_1_、09_2_这样的格式
    script_name = f"09_{script_num}_IF2_stitch_{protein}.srp"
    macro_name = f"09_{script_num}_IF2_Macro_{protein}.ijm"
    
    # Generate .srp script
    srp_script = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_stitch{protein}/stitch{protein}.%j.out
        #SBATCH -e logs_stitch{protein}/stitch{protein}.%j.err
        #SBATCH -J stitch{protein}
        #SBATCH -p C64M512G
        #SBATCH -c 16
        #SBATCH --time=24:00:00

        cp -v "{config['IF2_GLOBAL_STITCH']['registration_dir']}/IF1/{first_protein}/TileConfiguration.registered.txt" "{config['IF2_GLOBAL_STITCH']['registration_dir']}/IF2/{protein}/"

        source activate Fiji
        {config['IF2_GLOBAL_STITCH']['imagej_path']} --headless --console --run "$(pwd)/{script_name.replace('.srp', '.bsh')}"
    """)
    
    # Generate .bsh script
    bsh_script = textwrap.dedent(f"""\
        // Set MPICBG parameters
        mpicbg.stitching.GlobalOptimization.ignoreZ = true;
        print("Set mpicbg.stitching.GlobalOptimization.ignoreZ = true;");

        // Import IJ
        import ij.IJ;

        // Run macro script
        String macroPath = "{macro_name}";
        print("Running macro script: " + macroPath);
        IJ.runMacroFile(macroPath);
        print("Finished running macro script.");
    """)
    
    # Generate .ijm script
    ijm_script = textwrap.dedent(f"""\
        print("Starting Grid/Collection stitching...");

        run("Grid/Collection stitching", "type=[Positions from file] order=[Defined by TileConfiguration] directory={config['IF2_GLOBAL_STITCH']['registration_dir']}/IF2/{protein}/ layout_file=TileConfiguration.registered.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");

        print("Finished Grid/Collection stitching.");

        saveAs("Tiff", "{config['IF2_GLOBAL_STITCH']['registration_dir']}/IF2/{protein}/{protein}big3dnew.tif");

        run("Z Project...", "projection=[Max Intensity]");
        saveAs("Tiff", "{config['IF2_GLOBAL_STITCH']['registration_dir']}/IF2/{protein}/{protein}big2dnew.tif");

        close();
        close();
    """)
    
    return {
        script_name: srp_script,
        script_name.replace('.srp', '.bsh'): bsh_script,
        macro_name: ijm_script
    }

def generate_point_stitch_script(config, scripts_dir):
    """Generate point stitching script"""
    # 生成点拼接脚本
    point_stitch_script = os.path.join(scripts_dir, '10_stitchpoint.srp')
    script_content = textwrap.dedent(f"""\
        #!/bin/bash
        #SBATCH -o logs_stitchpoint/stitchpoint.%j.out
        #SBATCH -e logs_stitchpoint/stitchpoint.%j.err
        #SBATCH -J stitchpoint
        #SBATCH -p C64M512G
        #SBATCH -c 8
        #SBATCH --time=24:00:00

        module purge
        module load matlab/2023a

        MATLAB_SRC="{config['PROJECT']['matlab_src']}"
        MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
        CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
        export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

        PROJECT_NAME="{config['PROJECT']['project_name']}"
        PROJECT_ROOT="{config['PROJECT']['project_root']}"

        matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'stitchpoint', '$PROJECT_ROOT', '01_data', '02_registration', 'log')"
    """)
    with open(point_stitch_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    os.chmod(point_stitch_script, 0o755)
    print(f"生成点拼接脚本: {point_stitch_script}")
    return {'10_stitchpoint.srp': script_content}

def generate_stitchpoint_matlab_script(config):
    """生成stitchpointnewbjx.m文件"""
    # 从config中获取第一个蛋白名称
    first_protein = config['IF1_GLOBAL_STITCH']['proteins'].split(',')[0].strip()
    
    # 规范化路径
    stitch_file = os.path.normpath(f"{config['IF1_GLOBAL_STITCH']['registration_dir']}/IF1/{first_protein}/TileConfiguration.registered.txt")
    dapi_file = os.path.normpath(f"{config['IF1_GLOBAL_STITCH']['registration_dir']}/IF1/{first_protein}/{first_protein}big2dnew.tif")
    # 修改输出路径，移除02_registration目录
    spot_out_path = os.path.normpath(f"{config['IF1_GLOBAL_STITCH']['registration_dir'].replace('/02_registration', '')}/merged_spots")
    
    matlab_script = f"""% merge dots 
stitch_file = '{stitch_file}';
%% Setup the Import Options and import the data
opts = delimitedTextImportOptions("NumVariables", 6);

% Specify range and delimiter
opts.DataLines = [5, Inf];
opts.Delimiter = ["(", ")", ",", ";"];

% Specify column names and types
opts.VariableNames = ["Definetheimagecoordinates", "Var2", "Var3", "VarName4", "VarName5", "VarName6"];
opts.SelectedVariableNames = ["Definetheimagecoordinates", "VarName4", "VarName5", "VarName6"];
opts.VariableTypes = ["double", "string", "string", "double", "double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts.ConsecutiveDelimitersRule = "join";

% Specify variable properties
opts = setvaropts(opts, ["Var2", "Var3"], "WhitespaceRule", "preserve");
opts = setvaropts(opts, ["Var2", "Var3"], "EmptyFieldRule", "auto");
opts = setvaropts(opts, "Definetheimagecoordinates", "TrimNonNumeric", true);
opts = setvaropts(opts, "Definetheimagecoordinates", "ThousandsSeparator", ",");

% Import the data
TileConfiguration = readtable(stitch_file, opts);
TileConfiguration.Properties.VariableNames = {{'tile', 'x', 'y', 'z'}};
TileConfiguration.x = int32(fix(TileConfiguration.x));
TileConfiguration.y = int32(fix(TileConfiguration.y));
TileConfiguration.z = int32(fix(TileConfiguration.z));

head(TileConfiguration, 5)

%% Clear temporary variables
clear opts

% Global offsets 
offset_x = abs(min(TileConfiguration.x));
offset_y = abs(min(TileConfiguration.y));
offset_z = abs(min(TileConfiguration.z));

TileConfiguration.x = TileConfiguration.x + offset_x + 1;
TileConfiguration.y = TileConfiguration.y + offset_y + 1;
TileConfiguration.z = TileConfiguration.z + offset_z + 1;
%% Merge dots 


% load stitched dapi image
dapi_file = '{dapi_file}';
dapi_2d = imread(dapi_file);

if ndims(dapi_2d) == 3
    dapi_max = max(dapi_2d, [], 3);
else
    dapi_max = dapi_2d;
end

% create empty holders 
merged_points = int32([]);
merged_genes = {{}};
merged_region = [];
%%

for r=1:size(TileConfiguration,1)
    
    % get each row of tileconfig
    curr_row = table2cell(TileConfiguration(r, :));
    [tile, x, y, z] = curr_row{{:}};
    
    % load dots of each tile
    curr_position_dir = sprintf("Position%03d", tile);
    curr_dot_file = fullfile('{config['IF1_GLOBAL_STITCH']['registration_dir']}', curr_position_dir, "goodPoints_max3d.csv");
    tile_data = readtable(curr_dot_file); % Use readtable to read CSV file
    
    if ~isempty(tile_data)
        tile_goodSpots = tile_data{{:, 1:3}}; % Extract x, y, z columns
        tile_genes = tile_data{{:, 4}}; % Extract the gene information
        
        tile_goodSpots = int32(tile_goodSpots) + int32([x y z]);
     
        % construct dots region
        current_min = min(tile_goodSpots, [], 1);
        current_max = max(tile_goodSpots, [], 1);
        if current_max(1) > size(dapi_max, 2)
            current_max(1) = size(dapi_max, 2);
            toKeep = tile_goodSpots(:, 1) <= current_max(1);
            tile_goodSpots = tile_goodSpots(toKeep, :);
            tile_genes = tile_genes(toKeep);

        elseif current_max(2) > size(dapi_max, 1)
            current_max(2) = size(dapi_max, 1);   
            toKeep = tile_goodSpots(:, 2) <= current_max(2);
            tile_goodSpots = tile_goodSpots(toKeep, :);
            tile_genes = tile_genes(toKeep);

        end
        
        current_region = zeros(size(dapi_max));
        current_region(current_min(2):current_max(2), current_min(1):current_max(1)) = 1;

        % merge dots 
        if isempty(merged_region)
            merged_region = current_region;
        else
            current_overlap = merged_region & current_region;
            merged_region = merged_region | current_region;
            current_region = current_region - current_overlap; 
            
            temp_cell = num2cell(tile_goodSpots, 2); 
            current_lindex = cellfun(@(x) sub2ind([size(dapi_2d)], x(2), x(1)), temp_cell);
            current_logical = logical(current_region(current_lindex));
            tile_goodSpots = tile_goodSpots(current_logical, :);
            tile_genes = tile_genes(current_logical);
        end
        
        % save current 
        merged_points = [merged_points; tile_goodSpots];
        merged_genes = [merged_genes; cellstr(tile_genes)]; % Ensure gene information is a cell array of strings
    end
end
%%
merged_points(:,1) = merged_points(:,1) - 1;
merged_points(:,2) = merged_points(:,2) - 1;
merged_points(:,3) = merged_points(:,3) - 1;

%%
spot_out_path = '{spot_out_path}';

if ~exist(spot_out_path, 'dir')
    mkdir(spot_out_path)
end

% Convert merged_points to a table
merged_points_table = array2table(merged_points);

% Convert merged_genes to a table
merged_genes_table = cell2table(merged_genes, 'VariableNames', {{'Gene'}});

% Ensure the number of rows in both tables are the same
if height(merged_points_table) ~= height(merged_genes_table)
    error('The number of rows in merged_points_table and merged_genes_table must be the same.');
end

% Concatenate the tables
merged_table = [merged_points_table, merged_genes_table];

% Define column names for the table
merged_table.Properties.VariableNames = {{'x', 'y', 'z', 'Gene'}};

% Write to CSV
writetable(merged_table, fullfile(spot_out_path, 'merged_goodPoints_max3d.csv'));
"""
    return {'stitchpointnewbjx.m': matlab_script}

def generate_spot_finding_scripts(config):
    """Generate spot finding script for all subtiles"""
    array_tasks = int(config['LOCAL_REGISTRATION']['lr_array_tasks'])
    parallel_tasks = int(config['LOCAL_REGISTRATION']['lr_parallel_tasks'])
    
    scripts = []
    max_per_batch = 1000
    num_batches = (array_tasks + max_per_batch - 1) // max_per_batch
    
    for batch in range(num_batches):
        offset = batch * max_per_batch
        current_batch_size = min(max_per_batch, array_tasks - offset)
        array_range = f"1-{current_batch_size}"
        
        script = textwrap.dedent(f"""\
            #!/bin/bash
            #SBATCH -o logs_spot_finding/spot_finding_%A_%a.out  
            #SBATCH -e logs_spot_finding/spot_finding_%A_%a.err
            #SBATCH -J Spot_Finding
            #SBATCH -p C64M512G 
            #SBATCH -c 8        
            #SBATCH --mem=64G                  
            #SBATCH --time=24:00:00
            #SBATCH --array={array_range}%{parallel_tasks}

            module purge
            module load matlab/2023a

            MATLAB_SRC="{config['PROJECT']['matlab_src']}"
            MATLAB_ARCHIVE="{config['PROJECT']['matlab_archive']}"
            CORE_MATLAB_DIR="{config['PROJECT']['core_matlab_dir']}"
            export MATLAB_SRC MATLAB_ARCHIVE CORE_MATLAB_DIR

            PROJECT_NAME="{config['PROJECT']['project_name']}"
            PROJECT_ROOT="{config['PROJECT']['project_root']}"
            OFFSET=${{OFFSET:-{offset}}}  # 默认偏移为{offset}
            TASK_ID=$(( SLURM_ARRAY_TASK_ID + OFFSET ))
            SUBTILES_PER_POSITION={config['LOCAL_REGISTRATION']['sqrt_pieces']}*{config['LOCAL_REGISTRATION']['sqrt_pieces']}  
            POSITION_INDEX=$(( (TASK_ID - 1) / SUBTILES_PER_POSITION + 1 ))
            SUBTILE_ID=$(( (TASK_ID - 1) % SUBTILES_PER_POSITION + 1 ))
            POSITION_NAME=$(printf "Position%03d" $POSITION_INDEX)

            matlab -batch "addpath('$CORE_MATLAB_DIR'); core_matlab('$PROJECT_NAME', 'spot_finding', '$POSITION_NAME', {config['LOCAL_REGISTRATION']['image_width']}, {config['LOCAL_REGISTRATION']['image_depth']}, {config['LOCAL_REGISTRATION']['ref_round']}, {config['LOCAL_REGISTRATION']['channel_num']}, {config['LOCAL_REGISTRATION']['round_num']}, '$PROJECT_ROOT', '01_data', '02_registration', 'log', 'spotfinding_method', '{config['LOCAL_REGISTRATION']['spotfinding_method']}', 'sqrt_pieces', {config['LOCAL_REGISTRATION']['sqrt_pieces']}, 'subtile', $SUBTILE_ID, 'voxel_size', {config['LOCAL_REGISTRATION']['voxel_size']}, 'end_bases', {config['LOCAL_REGISTRATION']['end_bases']}, 'barcode_mode', '{config['LOCAL_REGISTRATION']['barcode_mode']}', 'split_loc', {config['LOCAL_REGISTRATION']['split_loc']}, 'intensity_threshold', {config['LOCAL_REGISTRATION']['intensity_threshold']})"
        """)
        scripts.append((f"03_spot_finding_batch{batch+1}.sh", script))
    
    return scripts

def generate_scripts(config_file='config.ini', script_dir='.'):
    """Generate all scripts"""
    # Get current script directory
    current_dir = Path(__file__).parent.absolute()
    
    # Build absolute paths for config file and script directory
    config_path = current_dir / config_file
    script_path = current_dir / script_dir
    
    if not config_path.exists():
        print(f"Error: Config file {config_path} does not exist")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Create script directory if it's not the current directory
    if script_dir != '.':
        script_path.mkdir(exist_ok=True)
    
    # Generate all scripts
    scripts = {
        '01_global_registration.sh': generate_global_registration_script(config),
        '04_local_stitch.sh': generate_local_stitch_script(config),
        '05_IF_registration.sh': generate_if_registration_script(config)
    }
    
    # Handle 02 scripts, which may return multiple scripts
    local_reg_scripts = generate_local_registration_script(config)
    if isinstance(local_reg_scripts, list):
        for script_name, content in local_reg_scripts:
            scripts[script_name] = content
    else:
        scripts['02_local_registration.sh'] = local_reg_scripts
    
    # Generate spot finding scripts
    spot_finding_scripts = generate_spot_finding_scripts(config)
    if isinstance(spot_finding_scripts, list):
        for script_name, content in spot_finding_scripts:
            scripts[script_name] = content
    
    # Check if IF2 registration script needs to be generated
    if config.getboolean('IF2_REGISTRATION', 'if2_enabled', fallback=False):
        scripts['05_IF2_registration.sh'] = generate_if2_registration_script(config)
    
    # Generate first stitching script
    first_stitch_scripts = generate_first_stitch_script(config)
    scripts.update(first_stitch_scripts)
    
    # Generate subsequent stitching scripts
    proteins = config['IF1_GLOBAL_STITCH']['proteins'].split(',')
    script_num = 1  # 从1开始
    for protein in proteins[1:]:  # Skip the first protein as it's already handled
        protein = protein.strip()
        subsequent_scripts = generate_subsequent_stitch_scripts(config, protein, script_num)
        scripts.update(subsequent_scripts)
        script_num += 1
    
    # Generate IF2 stitching scripts if enabled
    if config.getboolean('IF2_GLOBAL_STITCH', 'if2_enabled', fallback=False):
        proteins = config['IF2_GLOBAL_STITCH']['proteins'].split(',')
        script_num = 1  # 从1开始
        for protein in proteins:
            protein = protein.strip()
            if2_scripts = generate_if2_stitch_scripts(config, protein, script_num)
            scripts.update(if2_scripts)
            script_num += 1
    
    # Generate point stitching script
    point_scripts = generate_point_stitch_script(config, script_path)
    scripts.update(point_scripts)
    
    # Generate MATLAB stitchpoint script
    matlab_scripts = generate_stitchpoint_matlab_script(config)
    scripts.update(matlab_scripts)
    
    # Write all scripts
    for script_name, content in scripts.items():
        script_file = script_path / script_name
        with open(script_file, 'w') as f:
            f.write(content)
        os.chmod(script_file, 0o755)
        print(f"Generated script: {script_file}")
    
    return script_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="生成处理脚本")
    parser.add_argument('-c', '--config', 
                        type=str, 
                        default='config.ini',
                        help='配置文件路径（默认：config.ini）')
    parser.add_argument('-d', '--script-dir',
                        type=str,
                        default='.',
                        help='脚本输出目录（默认：当前目录）')
    
    args = parser.parse_args()
    generate_scripts(args.config, args.script_dir)