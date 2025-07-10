#!/bin/bash

# Create a temporary directory for individual sequence configs
mkdir -p Config/Sequence/temp

# List of EuRoC sequences
SEQUENCES=("MH01" "MH02" "MH03" "MH04" "MH05" "V101" "V102" "V103" "V201" "V202" "V203")

# Process each sequence
for SEQ in "${SEQUENCES[@]}"; do
    echo "Running sequence $SEQ"
    
    # Determine the path based on sequence name
    if [[ $SEQ == MH* ]]; then
        DIFFICULTY="easy"
        if [[ $SEQ == "MH03" ]]; then
            DIFFICULTY="medium"
        elif [[ $SEQ == "MH04" || $SEQ == "MH05" ]]; then
            DIFFICULTY="difficult"
        fi
        ROOT_PATH="/path/to/EuRoC/MH_${SEQ:2:2}_${DIFFICULTY}/mav0"
    elif [[ $SEQ == V* ]]; then
        DIFFICULTY="easy"
        if [[ $SEQ == "V103" || $SEQ == "V203" ]]; then
            DIFFICULTY="difficult"
        elif [[ $SEQ == "V102" || $SEQ == "V202" ]]; then
            DIFFICULTY="medium"
        fi
        ROOT_PATH="/path/to/EuRoC/V${SEQ:1:1}_${SEQ:2:2}_${DIFFICULTY}/mav0"
    fi
    
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