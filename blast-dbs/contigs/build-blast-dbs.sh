#!/usr/bin/env bash

#SBATCH --time 01:00:00
#SBATCH --mem 16G

megahit_dir=/scratch/cvw29/squirrel-shotgun/assemble-contigs/megahit-out/*
out_dir=/scratch/cvw29/squirrel-shotgun/blast-dbs/contigs/dbs

for sample_path in $megahit_dir
do
    sample=$(basename $sample_path)
    mkdir $out_dir/$sample

    makeblastdb \
    -in $sample_path/final.contigs.fa \
    -dbtype nucl \
    -out $out_dir/$sample/$sample \
    -max_file_sz 4GB
done
