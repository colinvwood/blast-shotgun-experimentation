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
        multiplicity_str = re.search(r"multi=[0-9]+\.[0-9]+ ", subject_str).group(0)
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
    blast_df = blast_df[blast_df["alignment length"] >= 0.20 * blast_df["query length"]]
    
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
