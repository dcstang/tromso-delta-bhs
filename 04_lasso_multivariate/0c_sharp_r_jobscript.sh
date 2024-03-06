#!/usr/bin/bash
#PBS -l walltime=24:00:00
#PBS -l select=1:ncpus=1:mem=24gb
#PBS -N rsharp
#PBS -o output/04_lasso_multivariate/
#PBS -e output/04_lasso_multivariate/
#PBS -J 1-10
# to change hardcoded outputs as necessary

module load anaconda3/personal
eval "$(conda shell.bash hook)"
conda activate hpcr

cd $PBS_O_WORKDIR
RSCRIPTPATH=$(head -1 temp_filepath.txt)
echo $RSCRIPTPATH
Rscript $RSCRIPTPATH
sleep 120
rm -f temp_filepath.txt