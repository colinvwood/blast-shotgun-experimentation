#!/usr/bin/env bash

#SBATCH --time 2-00:00:00
#SBATCH --ntasks 5
#SBATCH --cpus-per-task 8
#SBATCH --mem-per-cpu 2G

seqs_dir=/scratch/cvw29/squirrel-shotgun/host-alignment/bowtie-out
out_dir_base=/scratch/cvw29/squirrel-shotgun/assemble-contigs/megahit-out

for forward_file in $seqs_dir/retained-[0-9]*_R1_*fastq
do
    reverse_file=${forward_file/_R1_/_R2_}
    file_name=$(basename $forward_file .fastq)
    sample_name=${file_name/retained-/}
    merged_file=$seqs_dir/retained-merged-$sample_name.fastq

    out_dir=$out_dir_base/$sample_name
    
    srun --ntasks 1 -c 8 \
    megahit \
    -1 $forward_file \
    -2 $reverse_file \
    -r $merged_file \
    --num-cpu-threads 8 \
    --tmp-dir /scratch/cvw29/temp \
    -o $out_dir \
    &
done
wait
