#!/bin/bash

# Source directory containing the ground truth files
GT_SOURCE_DIR="/mnt/home/clin/ceph/dataset/tartan_test/stereo/tartanair_cvpr_gt/stereo_gt"

# Base directory for test sequences
TEST_DATA_DIR="/mnt/home/clin/ceph/dataset/tartan_test/stereo"

# List of sequences
SEQUENCES=("SE000" "SE001" "SE002" "SE003" "SE004" "SE005" "SE006" "SE007" 
           "SH000" "SH001" "SH002" "SH003" "SH004" "SH005" "SH006" "SH007")

# Process each sequence
for SEQ in "${SEQUENCES[@]}"; do
    echo "Processing $SEQ..."
    
    # Source file
    SRC_FILE="$GT_SOURCE_DIR/$SEQ.txt"
    
    # Destination directory and file
    DEST_DIR="$TEST_DATA_DIR/$SEQ"
    DEST_FILE="$DEST_DIR/pose_left.txt"
    
    # Check if source file exists
    if [ ! -f "$SRC_FILE" ]; then
        echo "Warning: Source file $SRC_FILE not found. Skipping."
        continue
    fi
    
    # Check if destination directory exists
    if [ ! -d "$DEST_DIR" ]; then
        echo "Warning: Destination directory $DEST_DIR not found. Skipping."
        continue
    fi
    
    # Copy and rename the file
    cp "$SRC_FILE" "$DEST_FILE"
    
    # Check if copy was successful
    if [ $? -eq 0 ]; then
        echo "Successfully copied $SEQ.txt to $DEST_FILE"
    else
        echo "Error: Failed to copy $SEQ.txt to $DEST_FILE"
    fi
done

echo "All ground truth files processed."
