# import pandas as pd

# df1 = pd.read_csv('movies_tmdb.tsv', sep='\t')
# df2 = pd.read_csv('movies_tmdb_reversed.tsv', sep='\t')

# merged_df = pd.d([df1, df2])


# # Save the merged dataframe to a new TSV file
# merged_df.to_csv('movies_tmdb_merged.tsv', sep='\t', index=False)

# print("Merged dataset saved to 'movies_tmdb_merged.tsv'")
import pandas as pd

# Load the datasets
df1 = pd.read_csv('movies_tmdb.tsv', sep='\t')
df2 = pd.read_csv('movies_tmdb_reversed.tsv', sep='\t')

# 1. Find rows in df1 but not in df2
diff_df1 = pd.merge(df1, df2, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
print("Rows in df1 but not in df2:")
print(diff_df1)

# 2. Find rows in df2 but not in df1
diff_df2 = pd.merge(df1, df2, how='outer', indicator=True).query('_merge == "right_only"').drop('_merge', axis=1)
print("\nRows in df2 but not in df1:")
print(diff_df2)

# 3. Symmetric difference (rows in either df1 or df2, but not both)
symmetric_diff = pd.concat([diff_df1, diff_df2])
print("\nSymmetric difference (rows unique to either df1 or df2):")
print(symmetric_diff)

# 4. Intersection (rows in both datasets)
intersection = pd.merge(df1, df2, how='inner')
print("\nIntersection (rows in both df1 and df2):")
print(intersection)
