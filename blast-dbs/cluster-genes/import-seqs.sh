#!/usr/bin/env bash

qiime tools import \
--input-path urease-subunit-beta-genes.fasta \
--output-path urease-subunit-beta-seqs.qza \
--type 'FeatureData[Sequence]'
