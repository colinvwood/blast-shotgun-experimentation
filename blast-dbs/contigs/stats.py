import os
import pandas as pd

alpha_abundances = []
for file in os.listdir('abundances/alpha'):
    sample = file.replace('-abundance.txt', '') 
    with open('abundances/alpha/' + file, 'r') as fh:
        abundance = fh.read().strip()
    alpha_abundances.append((sample, abundance))

beta_abundances = []
for file in os.listdir('abundances/beta'):
    sample = file.replace('-abundance.txt', '') 
    with open('abundances/beta/' + file, 'r') as fh:
        abundance = fh.read().strip()
    beta_abundances.append((sample, abundance))

gamma_abundances = []
for file in os.listdir('abundances/gamma'):
    sample = file.replace('-abundance.txt', '') 
    with open('abundances/gamma/' + file, 'r') as fh:
        abundance = fh.read().strip()
    gamma_abundances.append((sample, abundance))

contig_counts = []
for file in os.listdir('contig-counts/'):
    sample = file.replace('-counts.txt', '')
    with open('contig-counts/' + file, 'r') as fh:
        count = fh.read().strip()
    contig_counts.append((sample, count))

def create_dataframe(value_tuples, value_type):
    samples = []
    values = []
    for tuple_ in value_tuples:
        samples.append(tuple_[0])
        values.append(tuple_[1])

    return pd.DataFrame({'sample': samples, value_type: values})

alpha_abundance_df = create_dataframe(alpha_abundances, 'alpha abundance')
beta_abundance_df = create_dataframe(beta_abundances, 'beta abundance')
gamma_abundance_df = create_dataframe(gamma_abundances, 'gamma abundance')
contig_count_df = create_dataframe(contig_counts, 'contig count')

df = alpha_abundance_df.merge(beta_abundance_df, how='inner', on='sample')
df = df.merge(gamma_abundance_df, how='inner', on='sample')
df = df.merge(contig_count_df, how='inner', on='sample')

df['sample_id'] = df['sample'].str.replace('_L001_R1_001', '')
df.drop('sample', axis=1, inplace=True)

metadata_df = pd.read_csv('../../metadata/squirrel-diet-metadata.tsv', sep='\t')

df = df.merge(metadata_df, how='inner', on='sample_id')

df = df.astype({
    'contig count': float,
    'alpha abundance': float,
    'beta abundance': float,
    'gamma abundance': float,
})
df.drop('genwiz_id', axis=1, inplace=True)
df.drop('compartment', axis=1, inplace=True)

df['total scaled abundance'] = \
    (df['alpha abundance'] + df['beta abundance'] + df['gamma abundance']) * 100_000 \
    / df['contig count']

print(df.groupby('diet_type')['total scaled abundance'].mean())
print(df.groupby('reproduction_status')['total scaled abundance'].mean())
print(df.sort_values('diet_type').head(20))

df.to_csv('contigs-abundances.csv', index=False)

