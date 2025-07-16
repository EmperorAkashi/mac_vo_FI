#!/bin/bash
#SBATCH --job-name=macvo_run
#SBATCH --output=/mnt/home/clin/macvo_slurm_logs/macvo_run_%j.out
#SBATCH --error=/mnt/home/clin/macvo_slurm_logs/macvo_run_%j.err
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --gpus=2
#SBATCH --constraint=a100
#SBATCH -c 8
#SBATCH --mem=80gb
#SBATCH --time=16:00:00

# Create logs directory
mkdir -p /mnt/home/clin/macvo_slurm_logs

# Print some information about the job
echo "Running on host: $(hostname)"
echo "Starting at $(date)"
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"

# Load required modules
module purge
module load apptainer

# Define paths
DATASET_PATH="/mnt/home/clin/ceph/dataset"
PROJECT_PATH="/mnt/home/clin/ceph/projects/mac_vo_FI"
CONTAINER_PATH="/mnt/home/clin/macvo_latest.sif"

# Check if container exists
if [ ! -f "$CONTAINER_PATH" ]; then
    echo "Error: Container file not found at $CONTAINER_PATH"
    exit 1
fi

# Define which pipeline script to run (can be passed as an argument)
PIPELINE_SCRIPT=${1:-"run_euroc_pipeline.sh"}
echo "Running pipeline script: $PIPELINE_SCRIPT"

# Run the container with the specified pipeline script
apptainer run --nv \
    -B ${DATASET_PATH}:/data \
    -B ${PROJECT_PATH}:/home/macvo/workspace \
    ${CONTAINER_PATH} \
    /bin/bash -c "cd /home/macvo/workspace && ./${PIPELINE_SCRIPT}"

# Print job completion information
echo "Job completed at $(date)"
