#!/usr/bin/env bash

gene=alpha

qiime tools export \
--input-path urease-subunit-$gene-clustered-seqs.qza \
--output-path urease-subunit-$gene-clustered-seqs
