#!/bin/bash

# Create a temporary directory for individual sequence configs
mkdir -p Config/Sequence/temp

# Extract each sequence from TartanAir1_Test.yaml and run it
for SEQ in SE000 SE001 SE002 SE003 SE004 SE005 SE006 SE007 SH000 SH001 SH002 SH003 SH004 SH005 SH006 SH007; do
    echo "Running sequence $SEQ"
    
    # Create a temporary YAML file for this sequence
    cat > Config/Sequence/temp/${SEQ}.yaml << EOF
type: TartanAir_NoIMU
name: ${SEQ}
args:
    root: /data/tartan_test/stereo/${SEQ}
    compressed: true
    gtDepth: false
    gtPose: true
    gtFlow: false
EOF
    
    # Run MAC-VO on this sequence
    python3 MACVO.py --odom Config/Experiment/MACVO/MACVO_Performant.yaml --data Config/Sequence/temp/${SEQ}.yaml
done

# Clean up
rm -rf Config/Sequence/temp