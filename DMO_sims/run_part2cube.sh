#!/bin/bash

# This code is used to generate the coarsened density fields from ramses-DMO sims

# Load necessary modules
module load Stages/2024
module load Intel/2023.2.1

# Define the base directory for input files
input_base_dir="/p/oldscratch/lgreion/conaboy1/runs/LG_09_18/full_box/DMO_512"
# Define the base name for the output files
output_base_name="cube_"

# Loop over input files from 00001 to 00049
for i in $(seq -f "%05g" 10 49)
do
    # Define input and output file names
    input_file="${input_base_dir}/output_${i}"
    output_file="${output_base_name}${i}.dat"
    
    # Run the part2cube command
    /p/project/lgreion/david/ramses/utils/f90/part2cube -inp ${input_file} -out ${output_file} -lma 8 -nx 256 -ny 256 -nz 256

    # Optional: Print a message to indicate the progress
    echo "Processed ${input_file} to ${output_file}"
done
