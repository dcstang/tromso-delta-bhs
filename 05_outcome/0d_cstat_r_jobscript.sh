#!/usr/bin/bash
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=1:mem=4gb
#PBS -N cstat
#PBS -o output/05_outcome/
#PBS -e output/05_outcome/
#PBS -J 1-8

module load anaconda3/personal
eval "$(conda shell.bash hook)"
conda activate hpcr

cd $PBS_O_WORKDIR
RSCRIPTPATH=$(head -1 temp_cstat_filepath.txt)
echo $RSCRIPTPATH
Rscript $RSCRIPTPATH
rm -f temp_cstat_filepath.txt