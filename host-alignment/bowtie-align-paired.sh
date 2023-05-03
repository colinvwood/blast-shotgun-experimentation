#!/usr/bin/env bash

#SBATCH --time 8:00:00
#SBATCH --tasks 10
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu 6G

in_dir=/scratch/cvw29/squirrel-shotgun/diet-cecum-lumen-merged-demux
out_dir=/scratch/cvw29/squirrel-shotgun/host-alignment/bowtie-out
bowtie_index=/scratch/cvw29/squirrel-shotgun/host-alignment/urocitellus-parryii-bowtie-index/up

for forward_file in $in_dir/[0-9]*_R1_*fastq.gz
do
    reverse_file=${forward_file/_R1_/_R2_}
    paired_retained_file=$out_dir/retained-$(basename $forward_file)
    paired_filtered_file=$out_dir/filtered-$(basename $forward_file)

    srun --ntasks 1 --exclusive \
    bowtie2 -x $bowtie_index \
    -1 $forward_file \
    -2 $reverse_file \
    --un-conc $paired_retained_file \
    --al-conc $paired_filtered_file \
    -S /dev/null \
    &
done
wait
