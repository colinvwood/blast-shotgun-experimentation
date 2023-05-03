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

sample_depths = []
for file in os.listdir('fasta-reads/'):
    if 'combined' not in file:
        continue

    sample = file.replace('combined-', '')
    sample = sample.replace('.fasta', '')
    with open('fasta-reads/' + file, 'r') as fh:
        depth = len(fh.readlines()) / 2
    sample_depths.append((sample, depth))

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
sample_depths_df = create_dataframe(sample_depths, 'sample depth')

df = alpha_abundance_df.merge(beta_abundance_df, how='inner', on='sample')
df = df.merge(gamma_abundance_df, how='inner', on='sample')
df = df.merge(sample_depths_df, how='inner', on='sample')

df['sample_id'] = df['sample'].str.replace('_L001_R1_001', '')
df.drop('sample', axis=1, inplace=True)

metadata_df = pd.read_csv('../../metadata/squirrel-diet-metadata.tsv', sep='\t')
df = df.merge(metadata_df, how='inner', on='sample_id')

df = df.astype({
    'sample depth': float,
    'alpha abundance': float,
    'beta abundance': float,
    'gamma abundance': float,
})
df.drop('genwiz_id', axis=1, inplace=True)
df.drop('compartment', axis=1, inplace=True)

df['total scaled abundance'] = \
    (df['alpha abundance'] + df['beta abundance'] + df['gamma abundance']) * 100_000 \
    / df['sample depth']

print(df.groupby('diet_type')['total scaled abundance'].mean())
print(df.groupby('reproduction_status')['total scaled abundance'].mean())
print(df.sort_values('diet_type').head(20))

df.to_csv('reads-abundances.csv', index=False)



