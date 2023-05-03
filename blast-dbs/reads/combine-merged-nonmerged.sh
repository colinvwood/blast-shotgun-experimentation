#!/usr/bin/env bash

#SBATCH --time 00:20:00
#SBATCH --mem 4G

for forward_file in fasta-reads/[0-9]*_R1_*fasta
do

forward=$(basename $forward_file)
reverse=${forward/_R1_/_R2_}
merged=merged-$forward

cat fasta-reads/$forward fasta-reads/$reverse fasta-reads/$merged \
> fasta-reads/combined-$forward

done
