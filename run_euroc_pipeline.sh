#!/bin/bash

# Create a temporary directory for individual sequence configs
mkdir -p Config/Sequence/temp

# List of EuRoC sequences
SEQUENCES=("MH01" "MH02" "MH03" "MH04" "MH05" "V101" "V102" "V103" "V201" "V202" "V203")

# Process each sequence
for SEQ in "${SEQUENCES[@]}"; do
    echo "Running sequence $SEQ"
    
    # Convert sequence name to lowercase for path
    SEQ_LOWER=$(echo "$SEQ" | tr '[:upper:]' '[:lower:]')
    
    # Set the root path based on your naming convention
    ROOT_PATH="/data/euroc_mav/${SEQ_LOWER}"
    
    echo "Using path: $ROOT_PATH"
    
    # Create a temporary YAML file for this sequence
    cat > Config/Sequence/temp/${SEQ}.yaml << EOF
type: EuRoC_NoIMU
name: ${SEQ}
args:
    root: ${ROOT_PATH}
    gt_pose: true
EOF
    
    # Run MAC-VO on this sequence
    python3 MACVO.py --odom Config/Experiment/MACVO/MACVO_Performant.yaml --data Config/Sequence/temp/${SEQ}.yaml
done

# Clean up
rm -rf Config/Sequence/temp