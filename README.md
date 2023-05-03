## Notes on the shotgun pipeline used during Julita's visit


**Note**: only the core command from each step is shown, excluding the surrounding content of the bash scripts used on monsoon to submit them.

#### 1. adatper removal

```bash
qiime cutadapt trim-paired \
--i-demultiplexed-sequences diet-cecum-lumen-demux.qza \
--p-adapter-f AGATCGGAAGAGCACACGTCTGAACTCCAGTCA \
--p-adapter-r AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT \
--p-cores 24 \
--o-trimmed-sequences diet-cecum-lumen-adapter-trimmed-demux.qza
```
Notes:
- no quality filtering was done because the the quality plots indicated it wasn't necessary, but in general quality filtering should be a step here.


#### 2. merge reads

Qiime's vsearch wrapper could not be used because both the merged and unmerged reads were needed downstream, and the wrapper only returns the merged reads. The vsearch software itself was used instead.

```bash
vsearch --fastq_mergepairs $forward_file --reverse $reverse_file \
--fastqout $merged_out_file \
--fastqout_notmerged_fwd $forward_out_file \
--fastqout_notmerged_rev $reverse_out_file \
--eetabbedout $stats_file
```


#### 3. host read removal

**3.1 index host reference**
```bash
bowtie2-build urocitellus-parryii.fasta urocitellus-parryii-bowtie-index/up
```

**3.2 align merged reads**
```bash
bowtie2 -x $bowtie_index \
-U $merged_file \
--un $merged_retained_file \
--al $merged_filtered_file \
-S /dev/null
```

**3.3 align paired unmerged reads**
```bash
bowtie2 -x $bowtie_index \
-1 $forward_file \
-2 $reverse_file \
--un-conc $paired_retained_file \
--al-conc $paired_filtered_file \
-S /dev/null
```
Notes:
- the sam alignment files are discarded because they are not of interest
- the filtered reads are saved here, but are not used downstream, they could also have been discarded


#### 4. contig assembly

```bash
megahit \
-1 $forward_file \
-2 $reverse_file \
-r $merged_file \
--num-cpu-threads 8 \
--tmp-dir /scratch/cvw29/temp \
-o $out_dir
```
Notes:
- the temporary directory was explicitly parameterized because we have had run out of space in the default temporary directory location on our cluster


#### 5. build blast database from contigs

```bash
makeblastdb \
-in $sample_path/final.contigs.fa \
-dbtype nucl \
-out $out_dir/$sample/$sample \
-max_file_sz 4GB
```


#### 6. build blast database from reads

**6.1 convert fastq reads to fasta**
```bash
seqtk seq -A $fastq-file > fasta-reads/$sample.fasta
```
Notes:
- blast can not make nucleotide databases from fastq files

**6.2 combine merged and unmerged reads**
```bash
cat fasta-reads/$forward fasta-reads/$reverse fasta-reads/$merged \
> fasta-reads/combined-$forward
```

**6.3 build database from reads**
```bash
makeblastdb \
-in $sample_path \
-dbtype nucl \
-out $out_dir/$sample/$sample \
-max_file_sz 4GB
```


#### 7. retrieve genes of interest from ncbi

**7.1 search for records of interest**
```bash
esearch -db gene -query "tryptophan synthase" \
    | efilter -organism bacteria -source refseq \
    | efetch > $outfile
```
Notes:
- filtering for the refseq databse should help with redundancy and overall quality of the sequences, at the cost of the number of them

**7.2 downloads records from refseq**
```python
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
    cmd = "efetch -db nucleotide -id {} -seq_start {} -seq_stop {} " \
		  "-format fasta >> {}".format(accession, range_start, range_stop,
									   out_file)

    subprocess.run(cmd, shell=True)
```
Notes:
- this script is very fragile and makes several assumptions about how the records that are fetched in the above step are structured
- Only records with an 'NC_(...)' accession were used because these are retrievable from the nucleotide database under that id. 
- In general, the string matching from the esearch query to the ncbi database was fairly loose, so bespoke query filtering afterwards is probably a good idea


#### 8. cluster downloaded genes

```bash
qiime vsearch cluster-features-de-novo \
--i-sequences urease-subunit-$gene-seqs.qza \
--i-table urease-subunit-$gene-ft.qza \
--p-perc-identity 0.70 \
--o-clustered-table urease-subunit-$gene-clusterd-table.qza \
--o-clustered-sequences urease-subunit-$gene-clustered-seqs.qza
```
Notes:
- sequences had to first be imported into a qiime artifact
- a mock feature table had to be created to satisfy the `--i-table` parameter
- the clustered sequences then had to be exported back to raw fasta files for the blast querying step


#### 9. query blast database (either reads db or contigs db)

```bash
blastn \
-query ../cluster-genes/urease-subunit-$gene-clustered-seqs/dna-sequences.fasta \
-db dbs/$sample/$sample \
-task dc-megablast \
-outfmt "6 qseqid stitle qlen length sstart send evalue bitscore" \
-out results/$gene/urease-subunit-$gene-clustered-$sample-results.tsv
```


#### 10. calculate query abundance in sample (contigs)

```python
import sys
import re
import pandas as pd
def parse_blast_output(blast_file):
    return pd.read_csv(blast_file,
                       sep='\t',
                       header=None,
                       names=["query", "subject", "query length",
                       "alignment length", "subject start",
                       "subject end", "e value", "bit score"])

def add_multiplicity_column(blast_df):
    # split subject header into subject id and subject multiplicity
    def get_multiplicity(subject_str):
        multiplicity_str = re.search(r"multi=[0-9]+\.[0-9]+ ",
							         subject_str).group(0)
        return float(multiplicity_str.replace("multi=", ""))
  

    def get_subject_id(subject_str):
        return re.search(r"^.+? ", subject_str).group(0)

    blast_df["contig multiplicity"] = blast_df["subject"].apply(get_multiplicity)
    blast_df["subject"] = blast_df["subject"].apply(get_subject_id)

    return blast_df

def filter_alignments(blast_df):
    # only keep alignments with an e-value less than 1 x 10^-3 and where
    # the alignment length is at least one fifth of the query length
    blast_df = blast_df[blast_df["e value"] < 1e-3]

    blast_df = blast_df[blast_df["alignment length"] >= 0.20 \
	    * blast_df["query length"]]

    return blast_df

def filter_queries(blast_df):
    # for mulitple alignments to same contig, keep only the best one
    def find_best_alignment(df):
        best_align_score = 0
        for index, row in df.iterrows():
            if row["bit score"] > best_align_score:
                best_align_score = row["bit score"]
        return df[df["bit score"] >= best_align_score]

  
    blast_df = blast_df.groupby("subject").apply(find_best_alignment)
    blast_df.reset_index(drop=True, inplace=True)
  
    return blast_df
  
def get_total_sample_abundance(blast_df):
    return blast_df["contig multiplicity"].sum()

def main(args):
    blast_file = args[1]
    blast_df = parse_blast_output(blast_file)
    blast_df = add_multiplicity_column(blast_df)
    blast_df = filter_alignments(blast_df)
    blast_df = filter_queries(blast_df)
    abundance = get_total_sample_abundance(blast_df)
    print(abundance)
  
if __name__ == '__main__':
    main(sys.argv)
```
Notes:
- the implementation for the blast output generated from the **reads** database is slightly different
- multiple gene copies could occurr within a contig, so non-overlapping alignments within a contig could be retained instead of keeping only the best one, but this proved too complex to implement given the time constraint
- we only had moderate confidence in using contig multiplicty as a proxy for abundance, more research needs to be done to understand the exact interpretation, and there is a chance the interpretation changes from assembler to assembler


#### 11. merge abundance results with metadata and do stats...