import torch
import numpy as np
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from DataLoader import StereoFrame
from Module.Frontend.Matching import IMatcher
from Module.Frontend.StereoDepth import IStereoDepth
from Utility.PrettyPrint import Logger


class FrameMetricsCollector:
    """
    Collects per-frame metrics during MAC-VO execution and saves them to a CSV file.
    
    This class records metrics related to:
    - Flow quality and uncertainty
    - Stereo matching quality and uncertainty
    - 3D point uncertainty
    - Point filtering statistics
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the metrics collector.
        
        Args:
            output_dir: Directory where metrics will be saved
        """
        self.metrics: List[Dict[str, Any]] = []
        self.output_dir = output_dir
        self.output_path = output_dir / "frame_metrics.csv"
        Logger.write("info", f"Frame metrics will be saved to {self.output_path}")
    
    def record_frame_metrics(self, 
                           frame_idx: int,
                           timestamp: float,
                           frame: StereoFrame,
                           flow_data: Optional[IMatcher.Output] = None,
                           stereo_data: Optional[IStereoDepth.Output] = None,
                           point3d_covs: Optional[torch.Tensor] = None,
                           filtering_stats: Optional[Dict[str, int]] = None):
        """
        Record metrics for a single frame.
        
        Args:
            frame_idx: Index of the current frame
            timestamp: Timestamp of the current frame
            frame: The stereo frame being processed
            flow_data: Flow and uncertainty data from the frontend
            stereo_data: Stereo depth and uncertainty data from the frontend
            point3d_covs: 3D covariance matrices for tracked points
            filtering_stats: Statistics about point filtering
        """
        metrics = {
            "frame_idx": frame_idx,
            "timestamp": timestamp,
        }
        
        # Flow metrics
        if flow_data is not None and flow_data.flow is not None:
            with torch.no_grad():
                flow = flow_data.flow
                # Calculate flow magnitude (ignoring NaNs)
                valid_flow = ~torch.isnan(flow)
                if valid_flow.any():
                    flow_magnitude = torch.norm(flow[valid_flow.all(dim=1)], dim=1)
                    metrics.update({
                        "flow_magnitude_mean": float(flow_magnitude.mean().item()),
                        "flow_magnitude_std": float(flow_magnitude.std().item()),
                        "flow_coverage": float((valid_flow.all(dim=1).float().mean().item())),
                    })
                
                # Flow uncertainty
                if flow_data.cov is not None:
                    cov = flow_data.cov
                    valid_cov = ~torch.isnan(cov)
                    if valid_cov.any():
                        metrics.update({
                            "flow_uncertainty_mean": float(cov[valid_cov].mean().item()),
                            "flow_uncertainty_std": float(cov[valid_cov].std().item()),
                        })
        
        # Stereo metrics
        if stereo_data is not None:
            with torch.no_grad():
                # Depth metrics
                if stereo_data.depth is not None:
                    depth = stereo_data.depth
                    valid_depth = ~torch.isnan(depth)
                    if valid_depth.any():
                        metrics.update({
                            "depth_mean": float(depth[valid_depth].mean().item()),
                            "depth_std": float(depth[valid_depth].std().item()),
                            "depth_coverage": float(valid_depth.float().mean().item()),
                        })
                
                # Disparity metrics
                if stereo_data.disparity is not None:
                    disparity = stereo_data.disparity
                    valid_disp = ~torch.isnan(disparity)
                    if valid_disp.any():
                        metrics.update({
                            "disparity_mean": float(disparity[valid_disp].mean().item()),
                            "disparity_std": float(disparity[valid_disp].std().item()),
                        })
                
                # Disparity uncertainty
                if hasattr(stereo_data, 'disparity_uncertainty') and stereo_data.disparity_uncertainty is not None:
                    disp_uncertainty = stereo_data.disparity_uncertainty
                    valid_uncertainty = ~torch.isnan(disp_uncertainty)
                    if valid_uncertainty.any():
                        metrics.update({
                            "disparity_uncertainty_mean": float(disp_uncertainty[valid_uncertainty].mean().item()),
                            "disparity_uncertainty_std": float(disp_uncertainty[valid_uncertainty].std().item()),
                            "disparity_uncertainty_min": float(disp_uncertainty[valid_uncertainty].min().item()),
                            "disparity_uncertainty_max": float(disp_uncertainty[valid_uncertainty].max().item()),
                        })
                
                # Depth uncertainty
                if stereo_data.cov is not None:
                    depth_cov = stereo_data.cov
                    valid_cov = ~torch.isnan(depth_cov)
                    if valid_cov.any():
                        metrics.update({
                            "depth_uncertainty_mean": float(depth_cov[valid_cov].mean().item()),
                            "depth_uncertainty_std": float(depth_cov[valid_cov].std().item()),
                        })
        
        # 3D point uncertainty
        if point3d_covs is not None:
            with torch.no_grad():
                valid_covs = ~torch.isnan(point3d_covs).any(dim=(1, 2))
                if valid_covs.any():
                    # Calculate trace of covariance matrices (sum of diagonal elements)
                    cov_traces = torch.diagonal(point3d_covs[valid_covs], dim1=1, dim2=2).sum(dim=1)
                    metrics.update({
                        "point3d_uncertainty_mean": float(cov_traces.mean().item()),
                        "point3d_uncertainty_std": float(cov_traces.std().item()),
                    })
        
        # Filtering statistics
        if filtering_stats is not None:
            metrics.update({
                "initial_point_count": filtering_stats.get("initial_count", 0),
                "final_point_count": filtering_stats.get("final_count", 0),
                "rejection_rate": 1.0 - (filtering_stats.get("final_count", 0) / max(filtering_stats.get("initial_count", 1), 1)),
            })
        
        self.metrics.append(metrics)
    
    def save_metrics(self):
        """Save collected metrics to a CSV file."""
        if not self.metrics:
            Logger.write("warn", "No metrics to save")
            return
        
        try:
            df = pd.DataFrame(self.metrics)
            df.to_csv(self.output_path, index=False)
            Logger.write("info", f"Saved {len(self.metrics)} frame metrics to {self.output_path}")
        except Exception as e:
            Logger.write("error", f"Failed to save metrics: {e}")
