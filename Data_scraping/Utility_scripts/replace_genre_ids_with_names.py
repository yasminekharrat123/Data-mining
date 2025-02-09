import pandas as pd

def replace_genre_ids_with_names(merged_file, genre_file, output_file):
    merged_df = pd.read_csv(merged_file, sep="\t")
    genre_df = pd.read_csv(genre_file, sep="\t")
    genre_mapping = dict(zip(genre_df['id'], genre_df['name']))

    def map_genre_ids_to_names(genre_ids):
        if pd.isna(genre_ids):
            return ""
        ids = genre_ids.split(",")
        names = [genre_mapping.get(int(genre_id.strip()), "Unknown") for genre_id in ids]
        return ", ".join(names)

    merged_df['genre_ids'] = merged_df['genre_ids'].apply(map_genre_ids_to_names)

    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"Updated file saved to {output_file}")


if __name__ == "__main__":
    merged_file = "movies_tmdb_no_dup.tsv"
    genre_file = "movie_genre.tsv"
    output_file = "movies_tmdb_with_genres.tsv"
    replace_genre_ids_with_names(merged_file, genre_file, output_file)
