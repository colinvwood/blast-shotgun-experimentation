#!/usr/bin/env bash

#SBATCH --time 00:20:00
#SBATCH --mem 2G

outfile=tryptophan-synthase-records.txt

esearch -db gene -query "tryptophan synthase" \
    | efilter -organism bacteria -source refseq \
    | efetch > $outfile
