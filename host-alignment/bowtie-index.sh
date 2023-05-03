#!/usr/bin/env bash

#SBATCH --time 4:00:00
#SBATCH --mem 16G

bowtie2-build urocitellus-parryii.fasta urocitellus-parryii-bowtie-index/up
