#!/usr/bin/env bash

#SBATCH --time 12:00:00
#SBATCH --tasks 8
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu 8G

in_dir=/scratch/cvw29/squirrel-shotgun/diet-cecum-lumen-merged-demux
out_dir=/scratch/cvw29/squirrel-shotgun/host-alignment/bowtie-out
bowtie_index=/scratch/cvw29/squirrel-shotgun/host-alignment/urocitellus-parryii-bowtie-index/up

for merged_file in $in_dir/merged*_R1_*fastq.gz
do
    merged_retained_file=$out_dir/retained-$(basename $merged_file)
    merged_filtered_file=$out_dir/filtered-$(basename $merged_file)

    srun --ntasks 1 --exclusive \
    bowtie2 -x $bowtie_index \
    -U $merged_file \
    --un $merged_retained_file \
    --al $merged_filtered_file \
    -S /dev/null \
    &
done
wait
