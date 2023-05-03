#!/usr/bin/env bash

#SBATCH --time 00:30:00
#SBATCH --mem 4G

gene=alpha

for sample_path in dbs/*
do
    sample=$(basename $sample_path)

    blastn \
    -query ../cluster-genes/urease-subunit-$gene-clustered-seqs/dna-sequences.fasta \
    -db dbs/$sample/$sample \
    -task dc-megablast \
    -outfmt "6 qseqid stitle qlen length sstart send evalue bitscore" \
    -out results/$gene/urease-subunit-$gene-clustered-$sample-results.tsv
done
