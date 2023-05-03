#!/usr/bin/env bash

#SBATCH --time 00:05:00
#SBATCH --mem 2G

gene=alpha

module load anaconda3
conda activate qiime2-2023.2

qiime vsearch cluster-features-de-novo \
--i-sequences urease-subunit-$gene-seqs.qza \
--i-table urease-subunit-$gene-ft.qza \
--p-perc-identity 0.70 \
--o-clustered-table urease-subunit-$gene-clusterd-table.qza \
--o-clustered-sequences urease-subunit-$gene-clustered-seqs.qza
