#!/usr/bin/env bash

#SBATCH --time 12:00:00
#SBATCH --ntasks 8
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu 8G

out_dir=diet-cecum-lumen-merged-demux

for forward_file in ./diet-cecum-lumen-adapter-trimmed-demux/*_R1_*fastq.gz
do
    reverse_file=${forward_file/_R1_/_R2_}
    merged_out_file=$out_dir/merged-$(basename $forward_file)
    forward_out_file=$out_dir/$(basename $forward_file)
    reverse_out_file=$out_dir/$(basename $reverse_file)
    stats_file=$out_dir/stats-$(basename $forward_file .fastq.gz).txt

    srun --ntasks 1 --exclusive \
    vsearch --fastq_mergepairs $forward_file --reverse $reverse_file \
    --fastqout $merged_out_file \
    --fastqout_notmerged_fwd $forward_out_file \
    --fastqout_notmerged_rev $reverse_out_file \
    --eetabbedout $stats_file \
    &
done
wait
