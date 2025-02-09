import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

file_path = './movies.tsv'

df = pd.read_csv(file_path, sep='\t')

movie_ids = df.iloc[:, 0].tolist()

def scrape_box_office(movie_id):
    url = f'https://www.boxofficemojo.com/title/{movie_id}/'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {movie_id}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    data = {}
    data["Id"]=movie_id
    title_section = soup.find('h1', class_='a-size-extra-large')
    if title_section:
        title = title_section.text.strip()
        data['Title'], data['Year'] = title.split('(')[0].strip(), title.split('(')[1].strip(')') if title else "none"
    # Synopsis
    synopsis_section = soup.find('span', class_='a-size-medium')
    data['Synopsis'] = synopsis_section.text.strip() if synopsis_section else "none"

    # All Releases (Domestic, International, Worldwide)
    releases = soup.select('.mojo-performance-summary .a-section')
    if releases:
        for release in releases:
            key = release.find('span', class_='a-size-small').text.strip()
            value = release.find('span', class_='money')
            if value :
                data[key] = value.text.strip()
            else :
                data[key] = "none"
    else:
      data["Domestic"]= "none"
      data["International"]= "none"
      data["Worldwide"]= "none"

    # Domestic Distributor
    domestic_distributor = soup.find('div', class_='mojo-summary-values')
    if domestic_distributor:
        distributor = domestic_distributor.find('span', string='Domestic Distributor')
        data['Domestic Distributor'] = distributor.find_next_sibling('span').text.replace('See full company information', '').strip() if distributor else "none"
    else:
        data['Domestic Distributor']="none"

    # Domestic Opening
    domestic_opening = soup.find('div', class_='mojo-summary-values')
    if domestic_opening:
        opening_section = domestic_opening.find('span', string='Domestic Opening')
        if opening_section:
            sibling = opening_section.find_next_sibling('span')
            if sibling:
                # Clean up text by stripping unwanted whitespace and removing unnecessary parts
                raw_opening = sibling.text.strip()
                data['Domestic Opening'] = raw_opening.split('\n')[0].strip()
            else:
                data['Domestic Opening'] = "none"
        else:
            data['Domestic Opening'] = "none"
    else:
        data['Domestic Opening'] = "none"


    details = soup.find_all('div', class_='mojo-summary-values')
    for detail in details:
        mpaa = detail.find('span', string='MPAA')
        running_time = detail.find('span', string='Running Time')
        budget = detail.find('span', string='Budget')
        earliest_release_date = detail.find('span', string='Earliest Release Date')
        data['MPAA'] = mpaa.find_next_sibling('span').text.strip() if mpaa else "none"
        data['Running Time'] = running_time.find_next_sibling('span').text.strip() if running_time else "none"
        data['Budget'] = budget.find_next_sibling('span').text.strip() if budget else "none"
        if earliest_release_date:
            earliest_release_date_text = earliest_release_date.find_next_sibling('span').text.strip()
            data['Earliest Release Date'] = ' '.join(earliest_release_date_text.split())
        else:
            data['Earliest Release Date'] = "none"

    # Genres
    genres = soup.find('div', class_='mojo-summary-values')
    if genres:
        genre_section = genres.find('span', string='Genres')
        if genre_section:
            sibling = genre_section.find_next_sibling('span')
            if sibling:
                raw_genres = sibling.text.strip()
                temp = [genre.strip() for genre in raw_genres.split('\n') if genre.strip()] 
                data['Genres'] = ','.join(temp)            
            else:
                data['Genres'] = "none"
        else:
            data['Genres'] = "none"
    else:
        data['Genres'] = "none"
    return data

def scrape_movies(start_id="tt0035423",output_file="scraped_data.tsv"):

    # Find the starting index based on the provided movie ID
    try:
        start_index = movie_ids.index(start_id)
    except ValueError:
        print(f"Start ID '{start_id}' not found in the movie_ids list.")
        return 


        # Iterate over movie IDs starting from start_index
    for movie_id in movie_ids[start_index:]:
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            try:
                print(f"Scraping data for movie ID: {movie_id}...")
                data = scrape_box_office(movie_id)
                if data:
                    writer.writerow(data.values())
            except Exception as e:
                print(f"Error scraping movie ID {movie_id}: {e}")


scrape_movies()

