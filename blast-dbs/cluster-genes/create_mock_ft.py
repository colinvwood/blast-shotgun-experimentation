import qiime2
import pandas as pd

#a = qiime2.Artifact.load('table.qza')

#df = a.view(pd.DataFrame)

feature_data = "urease-subunit-alpha-seqs.qza"
out_path = "urease-subunit-alpha-ft.qza"

fd = qiime2.Artifact.load(feature_data).view(pd.Series)
ft = pd.DataFrame([1]*len(fd.index), index=fd.index, columns=['s1'])
ft = ft.T

ft_a = qiime2.Artifact.import_data("FeatureTable[Frequency]", ft)
ft_a.save(out_path)
