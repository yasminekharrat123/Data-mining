import os
import csv
import time
import requests
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def fetch_movie_details(tconst, api_key):
    url = f"https://api.themoviedb.org/3/find/{tconst}?external_source=imdb_id"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            print("Rate limit reached. Retrying after delay...")
            time.sleep(5)  
            return fetch_movie_details(tconst, api_key)  
        response.raise_for_status()
        data = response.json()
        
        movie_results = data.get("movie_results", [])
        if movie_results:
            return movie_results[0]
        else:
            print(f"No movie details found for IMDb ID: {tconst}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching details for IMDb ID {tconst}: {e}")
        return None


def process_movies(input_file, merged_file, api_key):
    # Load the merged file to get existing IMDb IDs
    if os.path.exists(merged_file):
        merged_df = pd.read_csv(merged_file, sep="\t")
        existing_ids = set(merged_df["imdb_id"])
    else:
        existing_ids = set()
        with open(merged_file, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile, delimiter="\t")
            writer.writerow(["imdb_id", "tmdb_id", "title", "overview", "poster_path", "original_language", "genre_ids", "release_date", "popularity"])

    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")

        for row in reader:
            tconst = row.get("tconst")
            if not tconst:
                print("Missing tconst in input row. Skipping...")
                continue

            if tconst in existing_ids:
                print(f"IMDb ID {tconst} already exists in the merged file. Skipping...")
                continue

            print(f"Fetching details for IMDb ID: {tconst}")
            movie_details = fetch_movie_details(tconst, api_key)

            if movie_details:
                with open(merged_file, "a", newline="", encoding="utf-8") as outfile:
                    writer = csv.writer(outfile, delimiter="\t")
                    writer.writerow([
                        tconst, 
                        movie_details.get("id", ""),  # TMDB ID
                        movie_details.get("title", ""),  
                        movie_details.get("overview", ""),  
                        movie_details.get("poster_path", ""),  
                        movie_details.get("original_language", ""),  
                        ",".join(map(str, movie_details.get("genre_ids", []))),  
                        movie_details.get("release_date", ""),  
                        movie_details.get("popularity", "")  
                    ])
                print(f"Details saved for IMDb ID: {tconst}")
            else:
                print(f"Failed to fetch details for IMDb ID: {tconst}")


if __name__ == "__main__":
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("Error: TMDB_API_KEY environment variable not set.")
        exit(1)

    input_file = "movies.tsv"
    merged_file = "movies_tmdb_merged.tsv"

    print(f"Starting processing of {input_file}")
    process_movies(input_file, merged_file, api_key)
    print(f"Processing complete. Results saved to {merged_file}")
