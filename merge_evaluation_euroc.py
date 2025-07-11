#!/usr/bin/env python3
import os
import glob
import pandas as pd
import argparse
import re

def merge_evaluation_files(results_dir, output_file):
    """
    Find all evaluation.csv files in the results directory and merge them into a single CSV file.
    
    Args:
        results_dir: Root directory containing all sequence results
        output_file: Path to save the merged CSV file
    """
    print(f"Searching for evaluation.csv files in {results_dir}...")
    
    # Find all evaluation.csv files
    eval_files = []
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file == "evaluation.csv":
                eval_files.append(os.path.join(root, file))
    
    print(f"Found {len(eval_files)} evaluation files.")
    
    if not eval_files:
        print("No evaluation files found. Exiting.")
        return
    
    # Read and merge all CSV files
    dfs = []
    for file in eval_files:
        # Extract sequence name from path
        # Format: .../MACVO-Performant@SEQNAME/timestamp/evaluation.csv
        seq_name = os.path.basename(os.path.dirname(os.path.dirname(file)))
        
        try:
            df = pd.read_csv(file)
            
            # Keep only the first row (skip the "Average" row)
            if len(df) > 1:
                df = df.iloc[[0]]
            
            # Add sequence name if not already in the data
            if "Trajectory" in df.columns and not df["Trajectory"].str.contains(seq_name).any():
                df["Trajectory"] = seq_name
                
            dfs.append(df)
            print(f"Added data from {seq_name}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not dfs:
        print("Failed to read any evaluation files. Exiting.")
        return
    
    # Combine all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Extract sequence type and number for sorting
    def extract_seq_info(trajectory):
        # Try to match MH sequences (MH01, MH02, etc.)
        mh_match = re.search(r'MH(\d+)', trajectory)
        if mh_match:
            return 'MH', int(mh_match.group(1))
        
        # Try to match V1 sequences (V101, V102, etc.)
        v1_match = re.search(r'V1(\d+)', trajectory)
        if v1_match:
            return 'V1', int(v1_match.group(1))
        
        # Try to match V2 sequences (V201, V202, etc.)
        v2_match = re.search(r'V2(\d+)', trajectory)
        if v2_match:
            return 'V2', int(v2_match.group(1))
        
        # Default case
        return 'Unknown', 999
    
    # Add sorting columns
    merged_df['seq_type'] = merged_df['Trajectory'].apply(lambda x: extract_seq_info(x)[0])
    merged_df['seq_num'] = merged_df['Trajectory'].apply(lambda x: extract_seq_info(x)[1])
    
    # Sort by sequence type and then by sequence number
    merged_df = merged_df.sort_values(by=['seq_type', 'seq_num'])
    
    # Remove temporary sorting columns
    merged_df = merged_df.drop(columns=['seq_type', 'seq_num'])
    
    # Save to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"Merged evaluation data saved to {output_file}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total sequences: {len(merged_df)}")
    print(f"Average RMSE_ATE: {merged_df['RMSE_ATE'].mean():.4f}")
    print(f"Average RMSE_RTE: {merged_df['RMSE_RTE'].mean():.4f}")
    print(f"Average RMSE_ROE: {merged_df['RMSE_ROE'].mean():.4f}")
    print(f"Average RMSE_RPE: {merged_df['RMSE_RPE'].mean():.4f}")
    
    # Print statistics by sequence type
    mh_df = merged_df[merged_df['Trajectory'].str.contains('MH')]
    v1_df = merged_df[merged_df['Trajectory'].str.contains('V1')]
    v2_df = merged_df[merged_df['Trajectory'].str.contains('V2')]
    
    if not mh_df.empty:
        print("\nMH Sequences Statistics:")
        print(f"Count: {len(mh_df)}")
        print(f"Average RMSE_ATE: {mh_df['RMSE_ATE'].mean():.4f}")
    
    if not v1_df.empty:
        print("\nV1 Sequences Statistics:")
        print(f"Count: {len(v1_df)}")
        print(f"Average RMSE_ATE: {v1_df['RMSE_ATE'].mean():.4f}")
    
    if not v2_df.empty:
        print("\nV2 Sequences Statistics:")
        print(f"Count: {len(v2_df)}")
        print(f"Average RMSE_ATE: {v2_df['RMSE_ATE'].mean():.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge MAC-VO evaluation results from multiple EuRoC sequences")
    parser.add_argument("--results_dir", type=str, default="/Users/chenlin/Downloads/datasets/euroc_mav/macvo_euroc_results/",
                        help="Directory containing all sequence results")
    parser.add_argument("--output", type=str, default="merged_euroc_evaluation.csv",
                        help="Output CSV file path")
    
    args = parser.parse_args()
    merge_evaluation_files(args.results_dir, args.output)
