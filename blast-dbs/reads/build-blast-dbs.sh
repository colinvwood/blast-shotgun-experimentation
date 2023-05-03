#!/usr/bin/env bash

#SBATCH --time 01:00:00
#SBATCH --ntasks 10
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu 6G

out_dir=/scratch/cvw29/squirrel-shotgun/blast-dbs/reads/dbs

for sample_path in fasta-reads/combined*
do
    sample=$(basename $sample_path .fasta)
    sample=${sample/combined-/}

    srun --ntasks 1 --cpus-per-task 1 \
    mkdir $out_dir/$sample && \
    makeblastdb \
    -in $sample_path \
    -dbtype nucl \
    -out $out_dir/$sample/$sample \
    -max_file_sz 4GB \
    &
done
wait
