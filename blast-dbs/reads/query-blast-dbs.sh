#!/usr/bin/env bash

#SBATCH --time 01:00:00
#SBATCH --ntasks 5
#SBATCH --cpus-per-task 1
#SBATCH --mem-per-cpu 8G

gene=gamma

for sample_path in dbs/*
do
    sample=$(basename $sample_path)

    srun --ntasks 1 --cpus-per-task 1 \
    blastn \
    -query ../cluster-genes/urease-subunit-$gene-clustered-seqs/dna-sequences.fasta \
    -db dbs/$sample/$sample \
    -task dc-megablast \
    -outfmt "6 qseqid stitle qlen length sstart send evalue bitscore" \
    -out results/$gene/urease-subunit-$gene-clustered-$sample-results.tsv \
    &
done
wait
