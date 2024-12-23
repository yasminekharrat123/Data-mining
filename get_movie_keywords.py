import pandas as pd
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("TMDB_API_KEY")
if not api_key:
    print("Error: TMDB_API_KEY environment variable not set.")
    exit(1)

def fetch_keywords(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            print("Rate limit reached. Retrying after delay...")
            time.sleep(5) 
            return fetch_keywords(movie_id)
        response.raise_for_status()
        data = response.json()
        keywords = [keyword["name"] for keyword in data.get("keywords", [])]
        return ", ".join(keywords) 
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch keywords for movie ID {movie_id}: {e}")
        return ""

df = pd.read_csv("movies_tmdb_with_genres.tsv", sep="\t")
output_file = "movies_tmdb_with_keywords.tsv"

if not os.path.exists(output_file):
    print('file is being created')
    df["keywords"] = ""
    df.head(0).to_csv(output_file, sep="\t", index=False)

start_id = "615684"  
start_processing = None 

for index, row in df.iterrows():
    movie_id = row.get("tmdb_id")


    # Skip rows until the starting TMDB ID is found
    if not start_processing:
        if str(movie_id) == str(start_id):
            start_processing = True
            print(f"Starting processing from TMDB ID: {start_id}")
        else:
            continue
    print(f"Fetching keywords for TMDB ID: {movie_id}")
    row["keywords"] = fetch_keywords(movie_id)
    row.to_frame().T.to_csv(output_file, sep="\t", index=False, header=False, mode='a')
    print(f"Row for TMDB ID {movie_id} appended to the file.")

print(f"Processing complete. Updated data saved to '{output_file}'.")
