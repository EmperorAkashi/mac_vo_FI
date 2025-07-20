#!/usr/bin/env python3
"""
Batch script to convert all MAC-VO pose files from .npy to .tum format.
This script searches for all result directories and converts both estimated poses
and ground truth poses to TUM format.
"""

import os
import sys
import glob
import argparse
import subprocess
from pathlib import Path


def find_result_directories(base_path):
    """Find all MAC-VO result directories containing poses.npy files."""
    result_dirs = []
    
    # Search pattern for MAC-VO result directories
    # Pattern: MACVO-Performant@<sequence>/<timestamp>/
    pattern = os.path.join(base_path, "MACVO-Performant@*", "*", "poses.npy")
    
    for poses_file in glob.glob(pattern):
        result_dir = os.path.dirname(poses_file)
        result_dirs.append(result_dir)
    
    return sorted(result_dirs)


def convert_poses(npy_2_tum_script, input_file, output_file):
    """Convert a single npy file to tum format."""
    if not os.path.exists(input_file):
        print(f"Warning: Input file not found: {input_file}")
        return False
    
    try:
        cmd = [
            "python", npy_2_tum_script,
            "--input", input_file,
            "--output", output_file
        ]
        
        print(f"Converting: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Successfully converted to {output_file}")
            return True
        else:
            print(f"  ✗ Failed to convert {input_file}")
            print(f"    Error: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to convert {input_file}")
        print(f"    Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"  ✗ Failed to convert {input_file}")
        print(f"    Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch convert MAC-VO pose files from npy to tum format")
    parser.add_argument("--results_dir", required=True, 
                       help="Base directory containing MAC-VO results (e.g., /path/to/macvo_euroc_results)")
    parser.add_argument("--npy_2_tum_script", default="npy_2_tum.py",
                       help="Path to npy_2_tum.py script (default: npy_2_tum.py)")
    parser.add_argument("--dry_run", action="store_true",
                       help="Show what would be converted without actually converting")
    
    args = parser.parse_args()
    
    # Check if npy_2_tum.py script exists
    if not os.path.exists(args.npy_2_tum_script):
        print(f"Error: npy_2_tum.py script not found at: {args.npy_2_tum_script}")
        print("Please provide the correct path using --npy_2_tum_script argument")
        sys.exit(1)
    
    # Check if results directory exists
    if not os.path.exists(args.results_dir):
        print(f"Error: Results directory not found: {args.results_dir}")
        sys.exit(1)
    
    # Find all result directories
    print(f"Searching for result directories in: {args.results_dir}")
    result_dirs = find_result_directories(args.results_dir)
    
    if not result_dirs:
        print("No MAC-VO result directories found!")
        sys.exit(1)
    
    print(f"Found {len(result_dirs)} result directories:")
    for result_dir in result_dirs:
        print(f"  {result_dir}")
    
    if args.dry_run:
        print("\n--- DRY RUN MODE ---")
        print("The following conversions would be performed:")
    
    print(f"\nStarting batch conversion...")
    
    total_conversions = 0
    successful_conversions = 0
    
    for result_dir in result_dirs:
        sequence_name = os.path.basename(os.path.dirname(result_dir)).split('@')[1]
        timestamp = os.path.basename(result_dir)
        
        print(f"\nProcessing {sequence_name} ({timestamp}):")
        
        # Convert estimated poses (poses.npy -> pose.tum)
        poses_npy = os.path.join(result_dir, "poses.npy")
        pose_tum = os.path.join(result_dir, "pose.tum")
        
        if args.dry_run:
            print(f"  Would convert: poses.npy -> pose.tum")
        else:
            total_conversions += 1
            if convert_poses(args.npy_2_tum_script, poses_npy, pose_tum):
                successful_conversions += 1
        
        # Convert ground truth poses (ref_poses.npy -> gt.tum)
        ref_poses_npy = os.path.join(result_dir, "ref_poses.npy")
        gt_tum = os.path.join(result_dir, "gt.tum")
        
        if os.path.exists(ref_poses_npy):
            if args.dry_run:
                print(f"  Would convert: ref_poses.npy -> gt.tum")
            else:
                total_conversions += 1
                if convert_poses(args.npy_2_tum_script, ref_poses_npy, gt_tum):
                    successful_conversions += 1
        else:
            print(f"  Note: No ground truth file found (ref_poses.npy)")
    
    if not args.dry_run:
        print(f"\nBatch conversion completed!")
        print(f"Successfully converted: {successful_conversions}/{total_conversions} files")
        
        if successful_conversions < total_conversions:
            print(f"Failed conversions: {total_conversions - successful_conversions}")
            sys.exit(1)
    else:
        print(f"\nDry run completed. Found {len(result_dirs)} directories to process.")


if __name__ == "__main__":
    main()
