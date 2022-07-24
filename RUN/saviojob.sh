#!/bin/bash
# Job name:
#SBATCH --job-name=test
#
# Account:
#SBATCH --account=fc_haeffnerbem
#
# Partition:
#SBATCH --partition=savio_bigmem
#
# Wall clock limit:
#SBATCH --time=00:01:00
#
module load python
source activate bem39
cd bem-savio/document
python BEMrun.py >& run.out
