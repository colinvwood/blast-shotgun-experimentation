#!/usr/bin/env bash

#SBATCH --job-name cutadapt-filter
#SBATCH --time 2-00:00:00
#SBATCH --mem 32G
#SBATCH --cpus-per-task 24

module load anaconda3
conda activate qiime2-2023.2

export TMP=/scratch/cvw29/temp
export TEMP=/scratch/cvw29/temp
export TMPDIR=/scratch/cvw29/temp

qiime cutadapt trim-paired \
--i-demultiplexed-sequences diet-cecum-lumen-demux.qza \
--p-adapter-f AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
--p-adapter-r AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
--p-cores 24 \
--o-trimmed-sequences diet-cecum-lumen-adapter-trimmed-demux.qza
