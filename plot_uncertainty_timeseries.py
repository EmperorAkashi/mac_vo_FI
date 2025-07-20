import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse

"""
Simple script to plot flow and point3d uncertainty metrics as time series with axis breaks for outliers.
"""


def plot_uncertainty_timeseries(csv_path, output_path=None, clip_percentile=95):
    """Load CSV and plot flow and point3d uncertainty time series with axis breaks."""
    
    # Load the CSV data
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} frames from {csv_path}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Flow uncertainty with axis break
    if 'flow_uncertainty_mean' in df.columns and 'flow_uncertainty_std' in df.columns:
        flow_mask = ~(df['flow_uncertainty_mean'].isna() | df['flow_uncertainty_std'].isna())
        if flow_mask.any():
            x = df.loc[flow_mask, 'frame_idx']
            mean_vals = df.loc[flow_mask, 'flow_uncertainty_mean']
            std_vals = df.loc[flow_mask, 'flow_uncertainty_std']
            
            # Calculate clip threshold
            clip_threshold = np.percentile(mean_vals, clip_percentile)
            max_val = mean_vals.max()
            
            # Plot the data
            ax1.plot(x, mean_vals, 'b-', linewidth=2, label='Flow Uncertainty Mean')
            ax1.fill_between(x, mean_vals - std_vals, mean_vals + std_vals, 
                           alpha=0.3, color='blue', label='±1 Std Dev')
            
            # Set y-axis limits and add axis break if needed
            if max_val > clip_threshold * 2:  # Only add break if outliers are significantly larger
                # Set main plot range to show most data clearly
                ax1.set_ylim(0, clip_threshold * 1.1)
                
                # Add text to indicate axis break
                ax1.text(0.02, 0.98, f'Axis break at {clip_threshold:.2f}\nMax value: {max_val:.2f}', 
                        transform=ax1.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
                
                # Add break marks on y-axis
                d = 0.015  # size of diagonal lines
                kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
                ax1.plot((-d, +d), (1-d, 1+d), **kwargs)  # top-left diagonal
                ax1.plot((-d, +d), (1-2*d, 1), **kwargs)  # top-right diagonal
            else:
                ax1.set_ylim(0, max_val * 1.1)
            
            ax1.set_title('Flow Uncertainty Over Time')
            ax1.set_xlabel('Frame Index')
            ax1.set_ylabel('Flow Uncertainty')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'No valid flow uncertainty data', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Flow Uncertainty Over Time (No Data)')
    else:
        ax1.text(0.5, 0.5, 'Flow uncertainty columns not found', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Flow Uncertainty Over Time (Columns Missing)')
    
    # Plot 2: Point3D uncertainty with axis break
    if 'point3d_uncertainty_mean' in df.columns and 'point3d_uncertainty_std' in df.columns:
        point3d_mask = ~(df['point3d_uncertainty_mean'].isna() | df['point3d_uncertainty_std'].isna())
        if point3d_mask.any():
            x = df.loc[point3d_mask, 'frame_idx']
            mean_vals = df.loc[point3d_mask, 'point3d_uncertainty_mean']
            std_vals = df.loc[point3d_mask, 'point3d_uncertainty_std']
            
            # Calculate clip threshold
            clip_threshold = np.percentile(mean_vals, clip_percentile)
            max_val = mean_vals.max()
            
            # Plot the data
            ax2.plot(x, mean_vals, 'r-', linewidth=2, label='Point3D Uncertainty Mean')
            ax2.fill_between(x, mean_vals - std_vals, mean_vals + std_vals, 
                           alpha=0.3, color='red', label='±1 Std Dev')
            
            # Set y-axis limits and add axis break if needed
            if max_val > clip_threshold * 2:  # Only add break if outliers are significantly larger
                # Set main plot range to show most data clearly
                ax2.set_ylim(0, clip_threshold * 1.1)
                
                # Add text to indicate axis break
                ax2.text(0.02, 0.98, f'Axis break at {clip_threshold:.2f}\nMax value: {max_val:.2f}', 
                        transform=ax2.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
                
                # Add break marks on y-axis
                d = 0.015  # size of diagonal lines
                kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
                ax2.plot((-d, +d), (1-d, 1+d), **kwargs)  # top-left diagonal
                ax2.plot((-d, +d), (1-2*d, 1), **kwargs)  # top-right diagonal
            else:
                ax2.set_ylim(0, max_val * 1.1)
            
            ax2.set_title('Point3D Uncertainty Over Time')
            ax2.set_xlabel('Frame Index')
            ax2.set_ylabel('Point3D Uncertainty')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No valid point3d uncertainty data', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Point3D Uncertainty Over Time (No Data)')
    else:
        ax2.text(0.5, 0.5, 'Point3D uncertainty columns not found', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Point3D Uncertainty Over Time (Columns Missing)')
    
    plt.tight_layout()
    
    # Save or show plot
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot flow and point3d uncertainty time series with axis breaks")
    parser.add_argument("csv_path", help="Path to frame metrics CSV file")
    parser.add_argument("--output", help="Output path for plot (optional, will show if not provided)")
    parser.add_argument("--clip_percentile", type=float, default=95, 
                       help="Percentile for axis break threshold (default: 95)")
    
    args = parser.parse_args()
    
    plot_uncertainty_timeseries(args.csv_path, args.output, args.clip_percentile)


if __name__ == "__main__":
    main()
