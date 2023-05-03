#!/usr/bin/env bash

#SBATCH --time 00:20:00
#SBATCH --mem 4G

for file in /scratch/cvw29/squirrel-shotgun/host-alignment/bowtie-out/*fastq
do

sample=$(basename $file .fastq)
sample=${sample/retained-/}

seqtk seq -A $file > fasta-reads/$sample.fasta 

done
