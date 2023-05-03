import pandas as pd

reads_df = pd.read_csv('reads/reads-abundances.csv')
contigs_df = pd.read_csv('contigs/contigs-abundances.csv')

df = reads_df.merge(contigs_df, how='inner', on='sample_id', suffixes=[' reads', ' contigs'])

df = df[['total scaled abundance reads', 'total scaled abundance contigs']]
print("spearman:")
print(df.corr(method='spearman'))
print("pearson:")
print(df.corr(method='pearson'))
print("kendall:")
print(df.corr(method='kendall'))
