#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess
import sys
from pathlib import Path

"""
Batch script to generate uncertainty time series plots for all MACVO-Performant results.
Automatically discovers all frame_metrics.csv files and generates corresponding plots.
"""

def find_frame_metrics_files(base_dir):
    """Find all frame_metrics.csv files in MACVO-Performant directories."""
    pattern = os.path.join(base_dir, "**/MACVO-Performant*/**/frame_metrics.csv")
    csv_files = glob.glob(pattern, recursive=True)
    
    # Sort for consistent processing order
    csv_files.sort()
    
    print(f"Found {len(csv_files)} frame_metrics.csv files:")
    for csv_file in csv_files:
        rel_path = os.path.relpath(csv_file, base_dir)
        print(f"  {rel_path}")
    
    return csv_files

def generate_output_path(csv_path):
    """Generate output plot path based on CSV path."""
    csv_dir = os.path.dirname(csv_path)
    output_path = os.path.join(csv_dir, "uncertainty_timeseries.png")
    return output_path

def plot_uncertainties(csv_path, output_path, plot_script_path, clip_percentile=95):
    """Run the uncertainty plotting script for a single CSV file."""
    cmd = [
        sys.executable, plot_script_path,
        csv_path,
        "--output", output_path,
        "--clip_percentile", str(clip_percentile)
    ]
    
    try:
        print(f"Generating plot: {os.path.relpath(output_path)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Print any output from the plotting script
        if result.stdout.strip():
            print(f"  Output: {result.stdout.strip()}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: Failed to generate plot")
        print(f"  Command: {' '.join(cmd)}")
        print(f"  Return code: {e.returncode}")
        if e.stdout:
            print(f"  Stdout: {e.stdout}")
        if e.stderr:
            print(f"  Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"  ERROR: Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Batch generate uncertainty time series plots for all MACVO-Performant results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all results in the default directory
  python batch_plot_uncertainties.py /path/to/macvo_euroc_results

  # Dry run to see what would be processed
  python batch_plot_uncertainties.py /path/to/macvo_euroc_results --dry-run

  # Use custom clipping percentile
  python batch_plot_uncertainties.py /path/to/macvo_euroc_results --clip-percentile 90
        """
    )
    
    parser.add_argument("results_dir", 
                       help="Base directory containing MACVO-Performant result directories")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be processed without actually generating plots")
    parser.add_argument("--clip-percentile", type=float, default=95,
                       help="Percentile for axis break threshold (default: 95)")
    parser.add_argument("--plot-script", default=None,
                       help="Path to plot_uncertainty_timeseries.py script (default: same directory as this script)")
    
    args = parser.parse_args()
    
    # Validate results directory
    if not os.path.isdir(args.results_dir):
        print(f"ERROR: Results directory does not exist: {args.results_dir}")
        sys.exit(1)
    
    # Determine plot script path
    if args.plot_script:
        plot_script_path = args.plot_script
    else:
        # Assume it's in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plot_script_path = os.path.join(script_dir, "plot_uncertainty_timeseries.py")
    
    if not os.path.isfile(plot_script_path):
        print(f"ERROR: Plot script not found: {plot_script_path}")
        sys.exit(1)
    
    print(f"Batch Uncertainty Plot Generator")
    print(f"Results directory: {args.results_dir}")
    print(f"Plot script: {plot_script_path}")
    print(f"Clip percentile: {args.clip_percentile}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # Find all frame_metrics.csv files
    csv_files = find_frame_metrics_files(args.results_dir)
    
    if not csv_files:
        print("No frame_metrics.csv files found in MACVO-Performant directories.")
        sys.exit(0)
    
    print()
    
    if args.dry_run:
        print("DRY RUN - Would generate the following plots:")
        for csv_path in csv_files:
            output_path = generate_output_path(csv_path)
            rel_csv = os.path.relpath(csv_path, args.results_dir)
            rel_output = os.path.relpath(output_path, args.results_dir)
            print(f"  {rel_csv} -> {rel_output}")
        print(f"\nTotal: {len(csv_files)} plots would be generated.")
        return
    
    # Process all files
    print("Processing files:")
    success_count = 0
    error_count = 0
    
    for i, csv_path in enumerate(csv_files, 1):
        output_path = generate_output_path(csv_path)
        rel_csv = os.path.relpath(csv_path, args.results_dir)
        
        print(f"[{i}/{len(csv_files)}] {rel_csv}")
        
        # Check if output already exists
        if os.path.exists(output_path):
            print(f"  Plot already exists: {os.path.relpath(output_path)}")
            print(f"  Overwriting...")
        
        # Generate the plot
        success = plot_uncertainties(csv_path, output_path, plot_script_path, args.clip_percentile)
        
        if success:
            success_count += 1
            print(f"  ✓ Success")
        else:
            error_count += 1
            print(f"  ✗ Failed")
        
        print()
    
    # Summary
    print("="*60)
    print(f"Batch processing complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"  Total: {len(csv_files)}")
    
    if error_count > 0:
        print(f"\n{error_count} plots failed to generate. Check the error messages above.")
        sys.exit(1)
    else:
        print(f"\nAll plots generated successfully!")

if __name__ == "__main__":
    main()
