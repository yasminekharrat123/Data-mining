import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_movie_details_omdb(imdb_id, api_key):
    url = f"http://www.omdbapi.com/?apikey={api_key}&i={imdb_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 429:
            print("Rate limit reached. Retrying after delay...")
            time.sleep(5)
            return fetch_movie_details_omdb(imdb_id, api_key)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") == "True":
            return data
        else:
            print(f"No movie details found for IMDb ID: {imdb_id}. Error: {data.get('Error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching details for IMDb ID {imdb_id}: {e}")
        return None

def process_movies_omdb(input_file, output_file, api_key, start_id=None):
    # Check if the file exists to determine if the header should be written
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, "a", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        if not file_exists:
            writer.writerow([
                "imdb_id", "title", "year", "rated", "released", 
                "runtime", "genre", "director", "writer", "actors", 
                "plot", "language", "country", "awards", "poster", 
                "metascore", "imdb_rating", "imdb_votes", "type", "dvd", 
                "box_office", "production", "website"
            ])
    
    start_processing = start_id is None
    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        
        for row in reader:
            imdb_id = row.get("tconst")
            if not imdb_id:
                print("Missing IMDb ID in input row. Skipping...")
                continue
            
            if not start_processing:
                if imdb_id == start_id:
                    start_processing = True
                else:
                    continue
            
            print(f"Fetching details for IMDb ID: {imdb_id}")
            movie_details = fetch_movie_details_omdb(imdb_id, api_key)
            
            if movie_details:
                with open(output_file, "a", newline="", encoding="utf-8") as outfile:
                    writer = csv.writer(outfile, delimiter="\t")
                    writer.writerow([
                        imdb_id,
                        movie_details.get("Title", ""),
                        movie_details.get("Year", ""),
                        movie_details.get("Rated", ""),
                        movie_details.get("Released", ""),
                        movie_details.get("Runtime", ""),
                        movie_details.get("Genre", ""),
                        movie_details.get("Director", ""),
                        movie_details.get("Writer", ""),
                        movie_details.get("Actors", ""),
                        movie_details.get("Plot", ""),
                        movie_details.get("Language", ""),
                        movie_details.get("Country", ""),
                        movie_details.get("Awards", ""),
                        movie_details.get("Poster", ""),
                        movie_details.get("Metascore", ""),
                        movie_details.get("imdbRating", ""),
                        movie_details.get("imdbVotes", ""),
                        movie_details.get("Type", ""),
                        movie_details.get("DVD", ""),
                        movie_details.get("BoxOffice", ""),
                        movie_details.get("Production", ""),
                        movie_details.get("Website", "")
                    ])
                print(f"Details saved for IMDb ID: {imdb_id}")
            else:
                print(f"Failed to fetch details for IMDb ID: {imdb_id}")

if __name__ == "__main__":
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        print("Error: OMDB_API_KEY environment variable not set.")
        exit(1)
    
    input_file = "movies.tsv"
    output_file = "movies_omdb.tsv"
    
    # Define the start ID here or use None to process all records.
    start_id = input("Enter start IMDb ID (or press Enter to start from the beginning): ").strip() or None

    print(f"Starting processing of {input_file}")
    process_movies_omdb(input_file, output_file, api_key, start_id)
    print(f"Processing complete. Results saved to {output_file}")
