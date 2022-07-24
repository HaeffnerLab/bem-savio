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
#SBATCH --time=00:10:00
#
module load python
source activate /global/home/groups/fc_haeffnerbem/bem39
python run.py -s >& run.out
