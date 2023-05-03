import os
import re
import subprocess


in_file = "tryptophan-synthase-records.txt"
out_file = "tryptophan-synthase-genes.fasta"
query = "tryptophan synthase"

with open(in_file, 'r') as fh:
    contents = fh.read()
    records = contents.split('\n\n')

retained = []
for record in records:
    if query in record and "Annotation" in record:
        retained.append(record)

accession_pattern = r"NC_[0-9\.]+"
range_pattern = r"\([0-9]+\.\.[0-9]+(, complement)?\)"
accessions_visited = []
for record in retained:
    accession_match = re.search(accession_pattern, record)
    range_str_match = re.search(range_pattern, record)
    if accession_match and range_str_match:
        accession = accession_match.group(0)
        range_str = range_str_match.group(0)
    else:
        continue
    
    if accession in accessions_visited:
        continue
    accessions_visited.append(accession)

    range_list = range_str.strip('()').split('..') 
    if "complement" in range_str:
        range_list[1] = range_list[1].replace(", complement", "")

    range_start, range_stop = range_list
    cmd = "efetch -db nucleotide -id {} -seq_start {} -seq_stop {} -format fasta >> {}".format(
        accession, range_start, range_stop, out_file)

    subprocess.run(cmd, shell=True)

