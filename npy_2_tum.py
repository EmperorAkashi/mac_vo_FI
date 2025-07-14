#!/usr/bin/env python3

import argparse
import numpy as np
import os

def convert_npy_to_tum(input_file, output_file, verbose=True):
    """
    Convert a trajectory stored in .npy format to TUM format.
    
    Args:
        input_file: Path to the .npy file
        output_file: Path where the TUM file will be saved
        verbose: Whether to print progress information
    """
    if verbose:
        print(f"Reading trajectory from: {input_file}")
    
    try:
        # Load the numpy file
        trajectory = np.load(input_file)
        
        if verbose:
            print(f"Loaded array with shape: {trajectory.shape}")
        
        # Check if the data has the right format
        if len(trajectory.shape) != 2:
            raise ValueError(f"Expected 2D array, got {len(trajectory.shape)}D")
        
        # Determine format based on columns
        n_cols = trajectory.shape[1]
        
        if verbose:
            print(f"Array has {n_cols} columns")
        
        # Different possible formats:
        # - [t, x, y, z, qx, qy, qz, qw] (8 columns, standard TUM)
        # - [x, y, z, qx, qy, qz, qw] (7 columns, no timestamp)
        # - [t, x, y, z, qw, qx, qy, qz] (8 columns, quaternion order swapped)
        
        if n_cols == 7:
            # No timestamp, add one
            if verbose:
                print("No timestamp column found, adding timestamps starting from 0")
            timestamps = np.arange(len(trajectory)).reshape(-1, 1)
            # Assume format is [x, y, z, qx, qy, qz, qw]
            tum_data = np.hstack((timestamps, trajectory))
            
        elif n_cols == 8:
            # Check if quaternion order needs to be swapped
            # In TUM format, quaternion should be [qx, qy, qz, qw]
            # If it's [qw, qx, qy, qz], we need to reorder
            
            # Heuristic: in most cases, qw is close to 1 and the largest component
            # Check if the 5th column (index 4) has larger values than the 8th column (index 7)
            if np.mean(np.abs(trajectory[:, 4])) > np.mean(np.abs(trajectory[:, 7])):
                if verbose:
                    print("Detected quaternion format [qw, qx, qy, qz], reordering to TUM format")
                # Reorder from [t, x, y, z, qw, qx, qy, qz] to [t, x, y, z, qx, qy, qz, qw]
                tum_data = np.column_stack((
                    trajectory[:, 0],  # timestamp
                    trajectory[:, 1:4],  # x, y, z
                    trajectory[:, 5:8],  # qx, qy, qz
                    trajectory[:, 4]   # qw
                ))
            else:
                # Already in TUM format
                tum_data = trajectory
        else:
            raise ValueError(f"Unexpected number of columns: {n_cols}. Expected 7 or 8.")
        
        # Save to TUM format
        if verbose:
            print(f"Saving TUM format trajectory to: {output_file}")
        
        np.savetxt(output_file, tum_data, fmt='%.9f')
        
        if verbose and os.path.exists(output_file):
            print(f"Successfully saved {len(tum_data)} poses to {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        
        return True
    
    except Exception as e:
        print(f"Error converting file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert NumPy trajectory files to TUM format")
    parser.add_argument("--input", "-i", required=True, help="Input .npy trajectory file")
    parser.add_argument("--output", "-o", required=True, help="Output TUM format file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")
    
    args = parser.parse_args()
    
    success = convert_npy_to_tum(args.input, args.output, verbose=not args.quiet)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
