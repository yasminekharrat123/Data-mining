from dotenv import load_dotenv
import os
import requests
import csv

load_dotenv()

def fetch_movie_genres(api_key, output_file):
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        genres = response.json().get("genres", [])
        
        if not genres:
            print("No genres found.")
            return
    
        with open(output_file, "w", newline="", encoding="utf-8") as tsv_file:
            writer = csv.writer(tsv_file, delimiter="\t")
            writer.writerow(["id", "name"])  # Header row
            for genre in genres:
                writer.writerow([genre["id"], genre["name"]])

        print(f"Movie genres saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key:
        print("Error: TMDB_API_KEY environment variable not set.")
    else:
        output_file = "movie_genre.tsv"
        fetch_movie_genres(api_key, output_file)
