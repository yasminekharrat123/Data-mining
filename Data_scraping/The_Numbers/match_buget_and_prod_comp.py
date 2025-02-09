import pandas as pd
from datetime import datetime

# Load the TSV files
file1 = pd.read_csv("./movies_181k.tsv", sep="\t")
file2 = pd.read_csv("./movies_prod_comp.tsv", sep="\t")

# Clean and preprocess the titles
file1['primaryTitle'] = file1['primaryTitle'].str.strip().str.lower()
file2['Movie'] = file2['Movie'].str.strip().str.lower()

# Standardize the date formats
file1['release_date'] = pd.to_datetime(file1['release_date'], format='%Y-%m-%d', errors='coerce')
file2['Release Date'] = pd.to_datetime(file2['Release Date'], format='%b %d, %Y', errors='coerce')

# Merge data based on the title and release date
merged = pd.merge(
    file1, 
    file2, 
    left_on=['primaryTitle', 'release_date'], 
    right_on=['Movie', 'Release Date'], 
    how='left', 
    suffixes=('', '_from_file2')
)

# Update columns only if they are missing in the first file
for col in ['budget', 'domestic', 'worldwide', 'domestic_opening']:
    merged[col] = merged[col].combine_first(merged[f'{col}_from_file2'])

# Handle production companies (append without duplication)
merged['distributor'] = merged['distributor'].combine_first(merged['Company'])
merged['distributor'] = merged['distributor'].apply(lambda x: ', '.join(set(x.split(', '))) if isinstance(x, str) else x)

# Drop extra columns from the second file
columns_to_drop = [col for col in merged.columns if col.endswith('_from_file2')]
merged.drop(columns=columns_to_drop, inplace=True)

# Save the merged file back to a TSV
merged.to_csv("merged_file.tsv", sep="\t", index=False)
